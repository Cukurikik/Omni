ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI VSSH ENGINE — Parallel SSH Execution & Fleet Management
# ===========================================================================
# Source Paradigm: https://github.com/yahoo/vssh
# Domain Layer  : Network (Parallel SSH)
# Zero-Mock     : 100% Native — subprocess, socket, json, os, sqlite3
# ===========================================================================
"""
vSSH teaches us:
  1. Parallel SSH execution across multiple hosts
  2. Connection pooling and reuse
  3. Command broadcast to host groups
  4. Output aggregation per host
  5. Timeout and error handling per host
  6. Host inventory management

This engine distills those paradigms into OMNI-native Python for
parallel SSH operations using subprocess and socket connectivity.
"""

import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class SSHHost:
    hostname: str
    port: int = 22
    user: str = ""
    group: str = "default"
    label: str = ""


@dataclass
class HostResult:
    hostname: str
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0
    reachable: bool = False
    error: str = ""


# ── SSH Executor ──────────────────────────────────────────────────────────

class SSHExecutor:
    """Execute SSH commands on single or multiple hosts."""

    @staticmethod
    def probe(host: str, port: int = 22, timeout: float = 5) -> Dict:
        try:
            start = time.perf_counter()
            with socket.create_connection((host, port), timeout=timeout) as s:
                latency = round((time.perf_counter() - start) * 1000, 2)
                banner = ""
                try:
                    s.settimeout(2)
                    banner = s.recv(256).decode("utf-8", errors="replace").strip()
                except Exception:
                    pass
                return {"host": host, "port": port, "reachable": True,
                        "latency_ms": latency, "banner": banner[:100]}
        except Exception as e:
            return {"host": host, "port": port, "reachable": False,
                    "error": str(e)[:128]}

    @staticmethod
    def execute_on_host(host: SSHHost, command: str, timeout: int = 30) -> HostResult:
        result = HostResult(hostname=host.hostname)
        probe = SSHExecutor.probe(host.hostname, host.port, timeout=5)
        result.reachable = probe.get("reachable", False)

        if not result.reachable:
            result.error = probe.get("error", "Unreachable")
            return result

        target = f"{host.user}@{host.hostname}" if host.user else host.hostname
        start = time.perf_counter()
        try:
            r = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
                 "-o", "BatchMode=yes", "-p", str(host.port), target, command],
                capture_output=True, text=True, timeout=timeout,
            )
            result.exit_code = r.returncode
            result.stdout = r.stdout[:4096]
            result.stderr = r.stderr[:2048]
        except FileNotFoundError:
            result.error = "ssh not installed"
        except subprocess.TimeoutExpired:
            result.error = f"Timeout ({timeout}s)"
        except Exception as e:
            result.error = str(e)[:256]
        result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return result

    @staticmethod
    def parallel_execute(hosts: List[SSHHost], command: str,
                          max_workers: int = 10, timeout: int = 30) -> List[HostResult]:
        results = []
        with ThreadPoolExecutor(max_workers=min(max_workers, len(hosts))) as pool:
            futures = {pool.submit(SSHExecutor.execute_on_host, h, command, timeout): h
                       for h in hosts}
            for future in as_completed(futures):
                results.append(future.result())
        return results

    @staticmethod
    def parallel_probe(hosts: List[SSHHost], max_workers: int = 20) -> List[Dict]:
        results = []
        with ThreadPoolExecutor(max_workers=min(max_workers, len(hosts))) as pool:
            futures = {pool.submit(SSHExecutor.probe, h.hostname, h.port): h
                       for h in hosts}
            for future in as_completed(futures):
                results.append(future.result())
        return results


# ── Host Inventory ────────────────────────────────────────────────────────

class HostInventory:
    """Manage SSH host inventory."""

    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".vssh_hosts.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".vssh_hosts.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                hostname TEXT PRIMARY KEY, port INTEGER,
                user_name TEXT, group_name TEXT, label TEXT,
                added_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exec_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT, command TEXT, exit_code INTEGER,
                duration_ms REAL, executed_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def add_host(self, host: SSHHost):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO hosts VALUES (?,?,?,?,?,?)",
                      (host.hostname, host.port, host.user,
                       host.group, host.label, time.time()))
        conn.commit()
        conn.close()

    def log_execution(self, result: HostResult, command: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO exec_log (hostname,command,exit_code,duration_ms,executed_at) VALUES (?,?,?,?,?)",
                      (result.hostname, command[:200], result.exit_code,
                       result.duration_ms, time.time()))
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM hosts")
        hosts = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM exec_log")
        execs = c.fetchone()[0]
        conn.close()
        return {"hosts": hosts, "executions": execs}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniVSSHEngine:
    """
    OMNI vSSH Engine — Zero-Mock Parallel SSH Execution.

    Capabilities (all native subprocess + socket + threading):
      - Multi-host SSH connectivity probing
      - Parallel command execution with ThreadPool
      - Host inventory management (SQLite)
      - Execution logging and audit trail
      - Output aggregation per host
    """

    def __init__(self):
        self.executor = SSHExecutor()
        self.inventory = HostInventory()

    def probe_hosts(self, hostnames: List[str], port: int = 22) -> Dict:
        hosts = [SSHHost(h, port) for h in hostnames]
        results = self.executor.parallel_probe(hosts)
        return {
            "probed": len(results),
            "reachable": sum(1 for r in results if r.get("reachable")),
            "results": results,
        }

    def diagnostics(self) -> Dict:
        ssh_ok = False
        try:
            r = subprocess.run(["ssh", "-V"], capture_output=True, text=True, timeout=5)
            ssh_ok = r.returncode == 0 or "OpenSSH" in r.stderr
        except FileNotFoundError:
            pass
        return {
            "engine": "OmniVSSHEngine",
            "status": "active",
            "ssh_installed": ssh_ok,
            "db": self.inventory.stats(),
            "capabilities": ["parallel_probe", "parallel_exec", "host_inventory",
                             "exec_log", "output_aggregate", "thread_pool"],
        }


if __name__ == "__main__":
    engine = OmniVSSHEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
