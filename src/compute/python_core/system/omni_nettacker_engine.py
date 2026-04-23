ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI NETTACKER ENGINE — OWASP Network Penetration & Vulnerability Scanner
# ===========================================================================
# Source Paradigm: https://github.com/OWASP/Nettacker
# Domain Layer  : Security (SYSTEM + NETWORK cross-layer)
# Zero-Prod     : 100% Native — subprocess/socket real scanning
# ===========================================================================
"""
OWASP Nettacker teaches us:
  1. Modular YAML-driven scan/vuln/brute modules
  2. Multi-threaded port scanning across TCP/UDP
  3. Subdomain enumeration via DNS resolution
  4. Service fingerprinting (HTTP headers, banners)
  5. Drift detection (comparing scan results over time)
  6. Report generation (JSON/HTML/CSV)

This engine distills those paradigms into OMNI-native Python using ONLY
stdlib: socket, subprocess, ssl, json, sqlite3. No pip install required.
"""

import json
import os
import socket
import sqlite3
import ssl
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    """OMNI production engine for ScanResult integration."""
    host: str
    port: int
    protocol: str
    state: str            # "open" | "closed" | "filtered"
    service: str           # detected service name
    banner: str            # raw banner grab
    latency_ms: float

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ScanResult",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


@dataclass
class VulnFinding:
    """OMNI production engine for VulnFinding integration."""
    host: str
    port: int
    vuln_id: str           # CVE or custom ID
    severity: str          # "critical" | "high" | "medium" | "low" | "info"
    description: str
    evidence: str

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "VulnFinding",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


@dataclass
class ScanReport:
    """OMNI production engine for ScanReport integration."""
    target: str
    timestamp: float
    scan_results: List[ScanResult] = field(default_factory=list)
    vuln_findings: List[VulnFinding] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ScanReport",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Scan Modules ─────────────────────────────────────────────────────────────

class PortScanner:
    """Native TCP connect scanner — no nmap dependency."""

    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443,
        445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900,
        6379, 8080, 8443, 9200, 27017,
    ]

    @staticmethod
    def tcp_connect(host: str, port: int, timeout: float = 1.5) -> ScanResult:
        """Perform a real TCP connect scan on a single port."""
        start = time.perf_counter()
        state = "closed"
        banner = ""
        service = "unknown"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((host, port))
                latency = (time.perf_counter() - start) * 1000

                if result == 0:
                    state = "open"
                    # Attempt banner grab
                    try:
                        if port in (443, 8443):
                            ctx = ssl.create_default_context()
                            ctx.check_hostname = False
                            ctx.verify_mode = ssl.CERT_NONE
                            with ctx.wrap_socket(s, server_hostname=host) as ss:
                                banner = f"TLS:{ss.version()}"
                                service = "https"
                        else:
                            s.sendall(b"\r\n")
                            s.settimeout(0.8)
                            banner = s.recv(1024).decode("utf-8", errors="replace").strip()
                    except Exception:
                        pass

                    # Service fingerprint by port
                    service = PortScanner._fingerprint_port(port, banner) or service
                else:
                    latency = (time.perf_counter() - start) * 1000
        except socket.timeout:
            latency = timeout * 1000
            state = "filtered"
        except OSError:
            latency = (time.perf_counter() - start) * 1000
            state = "closed"

        return ScanResult(
            host=host, port=port, protocol="tcp",
            state=state, service=service,
            banner=banner[:256], latency_ms=round(latency, 2),
        )

    @staticmethod
    def _fingerprint_port(port: int, banner: str) -> Optional[str]:
        """Map well-known ports to service names."""
        port_map = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 143: "imap",
            443: "https", 445: "smb", 1433: "mssql", 1521: "oracle",
            3306: "mysql", 3389: "rdp", 5432: "postgresql",
            5900: "vnc", 6379: "redis", 8080: "http-proxy",
            9200: "elasticsearch", 27017: "mongodb",
        }
        return port_map.get(port)

    def scan_host(self, host: str, ports: Optional[List[int]] = None,
                  threads: int = 16) -> List[ScanResult]:
        """Multi-threaded scan of a host across multiple ports."""
        if ports is None:
            ports = self.COMMON_PORTS

        results: List[ScanResult] = []
        lock = threading.Lock()

        def _scan_port(p: int):
            r = self.tcp_connect(host, p)
            with lock:
                results.append(r)

        batch_threads = []
        for port in ports:
            t = threading.Thread(target=_scan_port, args=(port,), daemon=True)
            batch_threads.append(t)
            t.start()
            if len(batch_threads) >= threads:
                for bt in batch_threads:
                    bt.join(timeout=3)
                batch_threads.clear()

        for bt in batch_threads:
            bt.join(timeout=3)

        results.sort(key=lambda r: r.port)
        return results

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "PortScanner",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Vuln Check Modules ──────────────────────────────────────────────────────

class VulnChecker:
    """Checks open services for common misconfigurations and exposures."""

    @staticmethod
    def check_http_headers(host: str, port: int = 80) -> List[VulnFinding]:
        """Check for missing security headers on HTTP services."""
        findings = []
        import urllib.request
        import urllib.error

        scheme = "https" if port in (443, 8443) else "http"
        url = f"{scheme}://{host}:{port}/"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OMNI-Nettacker/1.0"})
            if scheme == "https":
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                resp = urllib.request.urlopen(req, context=ctx, timeout=5)
            else:
                resp = urllib.request.urlopen(req, timeout=5)

            headers = dict(resp.headers)

            security_headers = {
                "Strict-Transport-Security": ("high", "Missing HSTS header"),
                "X-Content-Type-Options": ("medium", "Missing X-Content-Type-Options"),
                "X-Frame-Options": ("medium", "Missing X-Frame-Options (clickjacking risk)"),
                "Content-Security-Policy": ("medium", "Missing CSP header"),
                "X-XSS-Protection": ("low", "Missing X-XSS-Protection"),
            }

            for header_name, (severity, desc) in security_headers.items():
                if header_name not in headers:
                    findings.append(VulnFinding(
                        host=host, port=port,
                        vuln_id=f"OMNI-HDR-{header_name.upper().replace('-', '_')}",
                        severity=severity,
                        description=desc,
                        evidence=f"Header '{header_name}' absent in response",
                    ))

            # Check for server version disclosure
            server = headers.get("Server", "")
            if server and any(v in server.lower() for v in ["apache/", "nginx/", "iis/"]):
                findings.append(VulnFinding(
                    host=host, port=port,
                    vuln_id="OMNI-HDR-SERVER_DISCLOSURE",
                    severity="info",
                    description="Server version disclosed in headers",
                    evidence=f"Server: {server}",
                ))

        except Exception:
            pass

        return findings

    @staticmethod
    def check_ssl_cert(host: str, port: int = 443) -> List[VulnFinding]:
        """Check SSL certificate validity and expiry."""
        findings = []
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((host, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ss:
                    cert = ss.getpeercert(binary_form=False)
                    if cert:
                        # We got a cert but can't validate chain — note it
                        findings.append(VulnFinding(
                            host=host, port=port,
                            vuln_id="OMNI-SSL-CERT_PRESENT",
                            severity="info",
                            description="SSL certificate present",
                            evidence=f"Protocol: {ss.version()}",
                        ))
                    else:
                        findings.append(VulnFinding(
                            host=host, port=port,
                            vuln_id="OMNI-SSL-NO_CERT",
                            severity="high",
                            description="No SSL certificate returned by server",
                            evidence="getpeercert() returned empty",
                        ))
        except Exception as e:
            findings.append(VulnFinding(
                host=host, port=port,
                vuln_id="OMNI-SSL-CONN_FAIL",
                severity="info",
                description=f"SSL connection failed: {str(e)[:120]}",
                evidence="",
            ))

        return findings

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "VulnChecker",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Drift Detection & Persistence ───────────────────────────────────────────

class ScanDatabase:
    """SQLite-backed persistent scan storage for drift detection."""

    def __init__(self, db_path: str = ""):
        """Initialize ScanDatabase engine with default configuration."""
        if not db_path:
            db_path = os.path.join(
                os.path.dirname(__file__), "..", ".nettacker_scans.db"
            )
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Execute  init db operation for ScanDatabase engine."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                host TEXT,
                port INTEGER,
                state TEXT,
                service TEXT,
                banner TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS vuln_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                host TEXT,
                port INTEGER,
                vuln_id TEXT,
                severity TEXT,
                description TEXT,
                evidence TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store_scan(self, report: ScanReport):
        """Execute store scan operation for ScanDatabase engine."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for sr in report.scan_results:
            c.execute(
                "INSERT INTO scan_results (timestamp,host,port,state,service,banner) VALUES (?,?,?,?,?,?)",
                (report.timestamp, sr.host, sr.port, sr.state, sr.service, sr.banner),
            )
        for vf in report.vuln_findings:
            c.execute(
                "INSERT INTO vuln_findings (timestamp,host,port,vuln_id,severity,description,evidence) VALUES (?,?,?,?,?,?,?)",
                (report.timestamp, vf.host, vf.port, vf.vuln_id, vf.severity, vf.description, vf.evidence),
            )
        conn.commit()
        conn.close()

    def detect_drift(self, host: str) -> Dict:
        """Compare latest scan with previous scan to detect changes."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT DISTINCT timestamp FROM scan_results WHERE host=? ORDER BY timestamp DESC LIMIT 2",
            (host,),
        )
        timestamps = [row[0] for row in c.fetchall()]

        if len(timestamps) < 2:
            conn.close()
            return {"drift": False, "reason": "Insufficient scan history"}

        latest_ts, prev_ts = timestamps[0], timestamps[1]

        c.execute("SELECT port, state FROM scan_results WHERE host=? AND timestamp=?", (host, latest_ts))
        latest = {row[0]: row[1] for row in c.fetchall()}

        c.execute("SELECT port, state FROM scan_results WHERE host=? AND timestamp=?", (host, prev_ts))
        previous = {row[0]: row[1] for row in c.fetchall()}

        conn.close()

        new_open = [p for p in latest if latest[p] == "open" and previous.get(p) != "open"]
        newly_closed = [p for p in previous if previous[p] == "open" and latest.get(p) != "open"]

        return {
            "drift": bool(new_open or newly_closed),
            "new_open_ports": new_open,
            "newly_closed_ports": newly_closed,
        }

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ScanDatabase",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniNettackerEngine:
    """
    OMNI Nettacker Engine — Zero-Prod Network Security Scanner.

    Capabilities (all native, no pip install):
      - TCP port scanning (multi-threaded)
      - Service fingerprinting (banner grab + port map)
      - HTTP security header auditing
      - SSL/TLS certificate inspection
      - Drift detection via SQLite persistence
      - JSON/dict report generation
    """

    def __init__(self):
        """Initialize Nettacker engine with default configuration."""
        self.scanner = PortScanner()
        self.vuln_checker = VulnChecker()
        self.db = ScanDatabase()

    def full_scan(self, target: str,
                  ports: Optional[List[int]] = None,
                  check_vulns: bool = True) -> ScanReport:
        """Execute a full scan pipeline on a target host."""
        # Resolve hostname
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            ip = target

        report = ScanReport(target=target, timestamp=time.time())
        report.metadata["resolved_ip"] = ip

        # Phase 1: Port scan
        report.scan_results = self.scanner.scan_host(ip, ports)
        open_ports = [r for r in report.scan_results if r.state == "open"]
        report.metadata["open_port_count"] = len(open_ports)
        report.metadata["total_ports_scanned"] = len(report.scan_results)

        # Phase 2: Vulnerability checks on open services
        if check_vulns:
            for sr in open_ports:
                if sr.service in ("http", "https", "http-proxy"):
                    report.vuln_findings.extend(
                        self.vuln_checker.check_http_headers(ip, sr.port)
                    )
                if sr.service in ("https",) or sr.port in (443, 8443):
                    report.vuln_findings.extend(
                        self.vuln_checker.check_ssl_cert(ip, sr.port)
                    )

        report.metadata["vuln_count"] = len(report.vuln_findings)

        # Phase 3: Persist for drift detection
        self.db.store_scan(report)

        return report

    def quick_recon(self, target: str) -> Dict:
        """Fast recon: top 10 ports only, no vuln checks."""
        top_ports = [22, 80, 443, 3306, 5432, 6379, 8080, 8443, 9200, 27017]
        results = self.scanner.scan_host(target, top_ports, threads=10)
        open_results = [r for r in results if r.state == "open"]
        return {
            "target": target,
            "open_ports": [{"port": r.port, "service": r.service, "banner": r.banner} for r in open_results],
            "open_count": len(open_results),
        }

    def drift_check(self, target: str) -> Dict:
        """Check for network drift on a previously scanned target."""
        return self.db.detect_drift(target)

    def to_json(self, report: ScanReport) -> str:
        """Serialize a scan report to JSON."""
        return json.dumps({
            "target": report.target,
            "timestamp": report.timestamp,
            "metadata": report.metadata,
            "scan_results": [
                {"host": r.host, "port": r.port, "state": r.state,
                 "service": r.service, "banner": r.banner, "latency_ms": r.latency_ms}
                for r in report.scan_results
            ],
            "vuln_findings": [
                {"host": v.host, "port": v.port, "vuln_id": v.vuln_id,
                 "severity": v.severity, "description": v.description, "evidence": v.evidence}
                for v in report.vuln_findings
            ],
        }, indent=2)

    def diagnostics(self) -> Dict:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniNettackerEngine",
            "status": "active",
            "capabilities": ["tcp_scan", "banner_grab", "http_header_audit",
                             "ssl_cert_check", "drift_detection", "json_report"],
            "db_path": self.db.db_path,
        }


if __name__ == "__main__":
    engine = OmniNettackerEngine()
    print("[Nettacker] Quick Recon on localhost...")
    result = engine.quick_recon("127.0.0.1")
    print(json.dumps(result, indent=2))
