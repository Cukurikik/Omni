ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI AUTOBASE ENGINE — PostgreSQL HA Cluster Automation (DBaaS)
# ===========================================================================
# Source Paradigm: https://github.com/autobase-tech/autobase
# Domain Layer  : Domain (Database Infrastructure)
# Zero-Prod     : 100% Native — subprocess, socket, sqlite3, os
# ===========================================================================
"""
Autobase (formerly postgresql_cluster) teaches us:
  1. Automated PostgreSQL HA cluster deployment (Patroni + etcd)
  2. Connection pooling management (PgBouncer)
  3. Load balancing configuration (HAProxy)
  4. Automated failover and switchover
  5. Backup management with PITR (pg_basebackup, WAL-G)
  6. Health monitoring and drift detection
  7. Rolling upgrades without downtime

This engine distills those paradigms into OMNI-native Python for
PostgreSQL cluster lifecycle management using ONLY stdlib.
"""

import json
import os
import socket
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

class NodeRole(Enum):
    PRIMARY = "primary"
    REPLICA = "replica"
    WITNESS = "witness"
    UNKNOWN = "unknown"


class NodeStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"


@dataclass
class PgNode:
    host: str
    port: int = 5432
    role: NodeRole = NodeRole.UNKNOWN
    status: NodeStatus = NodeStatus.UNREACHABLE
    pg_version: str = ""
    data_dir: str = ""
    replication_lag_bytes: int = 0
    connections_active: int = 0
    connections_max: int = 100


@dataclass
class ClusterConfig:
    name: str
    nodes: List[PgNode] = field(default_factory=list)
    pgbouncer_port: int = 6432
    haproxy_port: int = 5000
    etcd_endpoints: List[str] = field(default_factory=list)
    backup_dir: str = "/var/lib/postgresql/backups"
    wal_level: str = "replica"
    max_wal_senders: int = 10
    synchronous_commit: str = "on"


@dataclass
class BackupInfo:
    backup_id: str
    timestamp: float
    size_bytes: int
    backup_type: str        # "full" | "incremental" | "wal"
    location: str
    status: str             # "completed" | "failed" | "in_progress"


# ── PostgreSQL Native Probe ─────────────────────────────────────────────────

class PgProbe:
    """Probe PostgreSQL instances using native socket/subprocess."""

    @staticmethod
    def tcp_check(host: str, port: int = 5432, timeout: float = 3.0) -> bool:
        """Check if a PostgreSQL port is reachable."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False

    @staticmethod
    def get_version(host: str, port: int = 5432) -> Optional[str]:
        """Get PostgreSQL version via psql subprocess."""
        try:
            result = subprocess.run(
                ["psql", "-h", host, "-p", str(port), "-U", "postgres",
                 "-t", "-A", "-c", "SELECT version();"],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "PGPASSWORD": os.environ.get("PGPASSWORD", "")},
            )
            if result.returncode == 0:
                return result.stdout.strip().split(",")[0]
        except Exception:
            pass
        return None

    @staticmethod
    def get_replication_status(host: str, port: int = 5432) -> Dict:
        """Query replication status from pg_stat_replication."""
        try:
            query = "SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn FROM pg_stat_replication;"
            result = subprocess.run(
                ["psql", "-h", host, "-p", str(port), "-U", "postgres",
                 "-t", "-A", "-F", "|", "-c", query],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "PGPASSWORD": os.environ.get("PGPASSWORD", "")},
            )
            if result.returncode == 0 and result.stdout.strip():
                replicas = []
                for line in result.stdout.strip().splitlines():
                    parts = line.split("|")
                    if len(parts) >= 4:
                        replicas.append({
                            "client": parts[0],
                            "state": parts[1],
                            "sent_lsn": parts[2],
                            "write_lsn": parts[3],
                        })
                return {"status": "ok", "replicas": replicas}
            return {"status": "no_replicas"}
        except FileNotFoundError:
            return {"status": "psql_not_found"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}

    @staticmethod
    def get_connection_stats(host: str, port: int = 5432) -> Dict:
        """Get active connection count."""
        try:
            query = "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
            result = subprocess.run(
                ["psql", "-h", host, "-p", str(port), "-U", "postgres",
                 "-t", "-A", "-c", query],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, "PGPASSWORD": os.environ.get("PGPASSWORD", "")},
            )
            if result.returncode == 0:
                return {"active_connections": int(result.stdout.strip())}
        except Exception:
            pass
        return {"active_connections": -1}


# ── Cluster Health Monitor ──────────────────────────────────────────────────

class ClusterHealthMonitor:
    """Monitor cluster health and detect anomalies."""

    def __init__(self):
        self.probe = PgProbe()

    def check_cluster(self, config: ClusterConfig) -> Dict:
        """Full health check of all nodes in a cluster."""
        report = {
            "cluster": config.name,
            "timestamp": time.time(),
            "nodes": [],
            "healthy": True,
            "primary_count": 0,
        }

        for node in config.nodes:
            reachable = self.probe.tcp_check(node.host, node.port)
            node_report = {
                "host": node.host,
                "port": node.port,
                "reachable": reachable,
                "role": node.role.value,
            }

            if reachable:
                node.status = NodeStatus.RUNNING
                version = self.probe.get_version(node.host, node.port)
                node_report["version"] = version or "unknown"
                conn_stats = self.probe.get_connection_stats(node.host, node.port)
                node_report["active_connections"] = conn_stats.get("active_connections", -1)

                if node.role == NodeRole.PRIMARY:
                    report["primary_count"] += 1
                    repl = self.probe.get_replication_status(node.host, node.port)
                    node_report["replication"] = repl
            else:
                node.status = NodeStatus.UNREACHABLE
                report["healthy"] = False

            node_report["status"] = node.status.value
            report["nodes"].append(node_report)

        # Validate: exactly one primary
        if report["primary_count"] != 1:
            report["healthy"] = False
            report["warning"] = f"Expected 1 primary, found {report['primary_count']}"

        return report


# ── Backup Manager ──────────────────────────────────────────────────────────

class BackupManager:
    """Manage PostgreSQL backups using pg_basebackup."""

    def __init__(self, backup_root: str = ""):
        if not backup_root:
            backup_root = os.path.join(os.path.dirname(__file__), "..", ".pg_backups")
        self.backup_root = backup_root
        os.makedirs(self.backup_root, exist_ok=True)
        self.db = self._init_catalog()

    def _init_catalog(self) -> str:
        db_path = os.path.join(self.backup_root, "backup_catalog.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                backup_id TEXT PRIMARY KEY,
                timestamp REAL,
                size_bytes INTEGER,
                backup_type TEXT,
                location TEXT,
                status TEXT,
                host TEXT,
                port INTEGER
            )
        """)
        conn.commit()
        conn.close()
        return db_path

    def create_backup(self, host: str, port: int = 5432,
                       label: str = "") -> Dict:
        """Execute pg_basebackup for a full base backup."""
        import hashlib
        backup_id = hashlib.sha256(f"{host}{port}{time.time()}".encode()).hexdigest()[:12]
        if not label:
            label = f"backup_{backup_id}"

        backup_dir = os.path.join(self.backup_root, backup_id)
        os.makedirs(backup_dir, exist_ok=True)

        try:
            result = subprocess.run(
                ["pg_basebackup", "-h", host, "-p", str(port),
                 "-U", "postgres", "-D", backup_dir,
                 "-Ft", "-z", "-l", label, "--checkpoint=fast"],
                capture_output=True, text=True, timeout=3600,
                env={**os.environ, "PGPASSWORD": os.environ.get("PGPASSWORD", "")},
            )

            if result.returncode == 0:
                # Calculate size
                total_size = sum(
                    os.path.getsize(os.path.join(dp, f))
                    for dp, dn, filenames in os.walk(backup_dir)
                    for f in filenames
                )
                self._record_backup(backup_id, host, port, total_size, "full", backup_dir, "completed")
                return {
                    "status": "success",
                    "backup_id": backup_id,
                    "location": backup_dir,
                    "size_bytes": total_size,
                }
            else:
                self._record_backup(backup_id, host, port, 0, "full", backup_dir, "failed")
                return {"status": "error", "stderr": result.stderr[:1024]}

        except FileNotFoundError:
            return {"status": "error", "message": "pg_basebackup not found on PATH"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}

    def _record_backup(self, backup_id, host, port, size, btype, location, status):
        conn = sqlite3.connect(self.db)
        conn.execute(
            "INSERT INTO backups VALUES (?,?,?,?,?,?,?,?)",
            (backup_id, time.time(), size, btype, location, status, host, port),
        )
        conn.commit()
        conn.close()

    def list_backups(self, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("SELECT * FROM backups ORDER BY timestamp DESC LIMIT ?", (limit,))
        cols = [d[0] for d in c.description]
        rows = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return rows


# ── Config Generator ────────────────────────────────────────────────────────

class ConfigGenerator:
    """Generate Patroni, PgBouncer, HAProxy configs for an HA cluster."""

    @staticmethod
    def patroni_config(node: PgNode, cluster_name: str,
                        etcd_endpoints: List[str]) -> Dict:
        """Generate Patroni YAML-equivalent config as a dict."""
        return {
            "scope": cluster_name,
            "name": f"{cluster_name}-{node.host.replace('.', '-')}",
            "restapi": {"listen": f"{node.host}:8008", "connect_address": f"{node.host}:8008"},
            "etcd3": {"hosts": ",".join(etcd_endpoints)},
            "bootstrap": {
                "dcs": {
                    "ttl": 30,
                    "loop_wait": 10,
                    "retry_timeout": 10,
                    "maximum_lag_on_failover": 1048576,
                    "postgresql": {
                        "use_pg_rewind": True,
                        "parameters": {
                            "wal_level": "replica",
                            "hot_standby": "on",
                            "max_wal_senders": 10,
                            "max_replication_slots": 10,
                        },
                    },
                },
            },
            "postgresql": {
                "listen": f"{node.host}:{node.port}",
                "connect_address": f"{node.host}:{node.port}",
                "data_dir": node.data_dir or f"/var/lib/postgresql/data/{cluster_name}",
                "authentication": {
                    "superuser": {"username": "postgres"},
                    "replication": {"username": "replicator"},
                },
            },
        }

    @staticmethod
    def pgbouncer_config(nodes: List[PgNode], pool_size: int = 20) -> str:
        """Generate PgBouncer INI config."""
        primary = next((n for n in nodes if n.role == NodeRole.PRIMARY), nodes[0])
        return f"""[databases]
* = host={primary.host} port={primary.port} dbname=postgres

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
pool_mode = transaction
default_pool_size = {pool_size}
max_client_conn = 500
"""

    @staticmethod
    def haproxy_config(nodes: List[PgNode]) -> str:
        """Generate HAProxy config for PostgreSQL load balancing."""
        backends = "\n".join(
            f"    server {n.host.replace('.', '-')} {n.host}:{n.port} check port {n.port}"
            for n in nodes
        )
        return f"""global
    maxconn 1000

defaults
    mode tcp
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend postgresql
    bind *:5000
    default_backend pg_nodes

backend pg_nodes
    option pgsql-check user postgres
{backends}
"""


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniAutobaseEngine:
    """
    OMNI Autobase Engine — Zero-Prod PostgreSQL HA Cluster Automation.

    Capabilities (all native stdlib):
      - PostgreSQL instance probing (TCP + psql subprocess)
      - Cluster health monitoring with replication status
      - Backup management via pg_basebackup
      - Config generation (Patroni, PgBouncer, HAProxy)
      - Backup catalog persistence (SQLite)
    """

    def __init__(self):
        self.probe = PgProbe()
        self.monitor = ClusterHealthMonitor()
        self.backup_mgr = BackupManager()
        self.config_gen = ConfigGenerator()

    def create_cluster_config(self, name: str,
                                hosts: List[Tuple[str, int]]) -> ClusterConfig:
        """Create a cluster configuration from host:port pairs."""
        nodes = []
        for i, (host, port) in enumerate(hosts):
            role = NodeRole.PRIMARY if i == 0 else NodeRole.REPLICA
            nodes.append(PgNode(host=host, port=port, role=role))
        return ClusterConfig(name=name, nodes=nodes)

    def health_check(self, config: ClusterConfig) -> Dict:
        """Run a full cluster health check."""
        return self.monitor.check_cluster(config)

    def backup(self, host: str, port: int = 5432) -> Dict:
        """Create a full backup of a PostgreSQL instance."""
        return self.backup_mgr.create_backup(host, port)

    def generate_configs(self, config: ClusterConfig) -> Dict:
        """Generate all HA infrastructure configs."""
        patroni_configs = [
            self.config_gen.patroni_config(n, config.name, config.etcd_endpoints)
            for n in config.nodes
        ]
        return {
            "patroni": patroni_configs,
            "pgbouncer": self.config_gen.pgbouncer_config(config.nodes),
            "haproxy": self.config_gen.haproxy_config(config.nodes),
        }

    def quick_probe(self, host: str, port: int = 5432) -> Dict:
        """Quick probe of a single PostgreSQL instance."""
        reachable = self.probe.tcp_check(host, port)
        result = {"host": host, "port": port, "reachable": reachable}
        if reachable:
            result["version"] = self.probe.get_version(host, port)
            result["connections"] = self.probe.get_connection_stats(host, port)
        return result

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniAutobaseEngine",
            "status": "active",
            "capabilities": ["pg_probe", "cluster_health", "backup_management",
                             "config_generation", "replication_monitoring"],
            "backup_root": self.backup_mgr.backup_root,
        }


if __name__ == "__main__":
    engine = OmniAutobaseEngine()
    print("[Autobase] Quick probe localhost:5432...")
    result = engine.quick_probe("127.0.0.1", 5432)
    print(json.dumps(result, indent=2))
