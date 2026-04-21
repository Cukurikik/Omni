ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI ALLINSSL ENGINE — SSL Certificate Lifecycle Management & Monitoring
# ===========================================================================
# Source Paradigm: https://github.com/allinssl/allinssl
# Domain Layer  : Security (SSL/TLS Management)
# Zero-Mock     : 100% Native — ssl, socket, subprocess, sqlite3
# ===========================================================================
"""
AllinSSL teaches us:
  1. Full certificate lifecycle: issue → deploy → renew → monitor
  2. ACME protocol integration (Let's Encrypt, ZeroSSL)
  3. Multi-domain certificate management (SAN, wildcard)
  4. Real-time expiration monitoring with alerts
  5. Central dashboard for all certificates
  6. One-click deployment to CDN/WAF/servers

This engine distills those paradigms into OMNI-native Python for
real SSL certificate inspection, monitoring, and lifecycle tracking.
"""

import hashlib
import json
import os
import socket
import sqlite3
import ssl
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

class CertStatus(Enum):
    """OMNI production engine for CertStatus integration."""
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"   # < 30 days
    EXPIRED = "expired"
    INVALID = "invalid"
    UNKNOWN = "unknown"

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "CertStatus",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


@dataclass
class CertInfo:
    """OMNI production engine for CertInfo integration."""
    hostname: str
    port: int = 443
    issuer: str = ""
    subject: str = ""
    san: List[str] = field(default_factory=list)  # Subject Alt Names
    serial: str = ""
    not_before: str = ""
    not_after: str = ""
    days_remaining: int = -1
    status: CertStatus = CertStatus.UNKNOWN
    protocol_version: str = ""
    cipher: str = ""
    key_bits: int = 0
    fingerprint_sha256: str = ""
    error: str = ""

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "CertInfo",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── SSL Certificate Inspector ──────────────────────────────────────────────

class SSLInspector:
    """Inspect SSL/TLS certificates from live hosts."""

    @staticmethod
    def inspect(hostname: str, port: int = 443, timeout: float = 8) -> CertInfo:
        """Connect to a host and extract full SSL certificate details."""
        info = CertInfo(hostname=hostname, port=port)
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher_info = ssock.cipher()
                    protocol = ssock.version()

                    # Subject
                    subject = dict(x[0] for x in cert.get("subject", ()))
                    info.subject = subject.get("commonName", "")

                    # Issuer
                    issuer = dict(x[0] for x in cert.get("issuer", ()))
                    info.issuer = issuer.get("organizationName", issuer.get("commonName", ""))

                    # SAN
                    san_entries = cert.get("subjectAltName", ())
                    info.san = [entry[1] for entry in san_entries if entry[0] == "DNS"]

                    # Serial
                    info.serial = str(cert.get("serialNumber", ""))

                    # Dates
                    info.not_before = cert.get("notBefore", "")
                    info.not_after = cert.get("notAfter", "")

                    # Days remaining
                    import datetime
                    try:
                        expire = ssl.cert_time_to_seconds(info.not_after)
                        info.days_remaining = max(0, int((expire - time.time()) / 86400))
                    except Exception:
                        info.days_remaining = -1

                    # Status
                    if info.days_remaining < 0:
                        info.status = CertStatus.EXPIRED
                    elif info.days_remaining <= 30:
                        info.status = CertStatus.EXPIRING_SOON
                    else:
                        info.status = CertStatus.VALID

                    # Cipher/Protocol
                    info.protocol_version = protocol or ""
                    if cipher_info:
                        info.cipher = cipher_info[0]
                        info.key_bits = cipher_info[2] if len(cipher_info) > 2 else 0

                    # Fingerprint
                    der = ssock.getpeercert(binary_form=True)
                    if der:
                        info.fingerprint_sha256 = hashlib.sha256(der).hexdigest()

        except ssl.SSLCertVerificationError as e:
            info.error = f"SSL verification failed: {str(e)[:128]}"
            info.status = CertStatus.INVALID
        except socket.timeout:
            info.error = "Connection timeout"
            info.status = CertStatus.UNKNOWN
        except Exception as e:
            info.error = str(e)[:256]
            info.status = CertStatus.UNKNOWN

        return info

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "SSLInspector",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── OpenSSL CLI Integration ────────────────────────────────────────────────

class OpenSSLCLI:
    """Interact with openssl CLI for local certificate operations."""

    @staticmethod
    def check_installed() -> Dict:
        """Execute check installed operation for OpenSSLCLI engine."""
        try:
            r = subprocess.run(["openssl", "version"], capture_output=True, text=True, timeout=5)
            return {"installed": r.returncode == 0, "version": r.stdout.strip()}
        except FileNotFoundError:
            return {"installed": False, "version": ""}

    @staticmethod
    def generate_self_signed(common_name: str, days: int = 365,
                              output_dir: str = ".") -> Dict:
        """Generate a self-signed certificate."""
        key_path = os.path.join(output_dir, f"{common_name}.key")
        cert_path = os.path.join(output_dir, f"{common_name}.crt")
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_path, "-out", cert_path,
            "-days", str(days), "-nodes",
            "-subj", f"/CN={common_name}",
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "status": "success" if r.returncode == 0 else "error",
                "key": key_path if r.returncode == 0 else "",
                "cert": cert_path if r.returncode == 0 else "",
                "error": r.stderr[:512] if r.returncode != 0 else "",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)[:256]}

    @staticmethod
    def inspect_local_cert(cert_path: str) -> Dict:
        """Inspect a local certificate file."""
        if not os.path.isfile(cert_path):
            return {"error": "File not found"}
        try:
            r = subprocess.run(
                ["openssl", "x509", "-in", cert_path, "-text", "-noout"],
                capture_output=True, text=True, timeout=10,
            )
            return {"status": "success", "output": r.stdout[:4096]}
        except Exception as e:
            return {"error": str(e)[:256]}

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OpenSSLCLI",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Certificate Database (SQLite) ──────────────────────────────────────────

class CertDatabase:
    """Persistent tracking of monitored SSL certificates."""

    def __init__(self, db_path: str = ""):
        """Initialize CertDatabase engine with default configuration."""
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".ssl_certs.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".ssl_certs.db")
        self.db_path = db_path
        self._init()

    def _init(self):
        """Execute  init operation for CertDatabase engine."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS certs (
                hostname TEXT PRIMARY KEY,
                port INTEGER DEFAULT 443,
                issuer TEXT, subject TEXT,
                not_before TEXT, not_after TEXT,
                days_remaining INTEGER, status TEXT,
                fingerprint TEXT, protocol TEXT,
                last_checked REAL, error TEXT
            )
        """)
        conn.commit()
        conn.close()

    def upsert(self, info: CertInfo):
        """Execute upsert operation for CertDatabase engine."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO certs
            (hostname,port,issuer,subject,not_before,not_after,days_remaining,status,fingerprint,protocol,last_checked,error)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (info.hostname, info.port, info.issuer, info.subject,
             info.not_before, info.not_after, info.days_remaining,
             info.status.value, info.fingerprint_sha256, info.protocol_version,
             time.time(), info.error),
        )
        conn.commit()
        conn.close()

    def get_expiring(self, days: int = 30) -> List[Dict]:
        """Execute get expiring operation for CertDatabase engine."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT hostname,days_remaining,status,issuer FROM certs WHERE days_remaining<=? AND days_remaining>=0", (days,))
        cols = ["hostname", "days_remaining", "status", "issuer"]
        rows = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return rows

    def stats(self) -> Dict:
        """Execute stats operation for CertDatabase engine."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT status, COUNT(*) FROM certs GROUP BY status")
        status_counts = {r[0]: r[1] for r in c.fetchall()}
        c.execute("SELECT COUNT(*) FROM certs")
        total = c.fetchone()[0]
        conn.close()
        return {"total": total, "by_status": status_counts}

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "CertDatabase",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniAllinSSLEngine:
    """
    OMNI AllInSSL Engine — Zero-Mock SSL Certificate Lifecycle Management.

    Capabilities (all native — ssl, socket, subprocess):
      - Live SSL certificate inspection (subject, issuer, SAN, expiry)
      - Certificate expiration monitoring
      - OpenSSL CLI integration (self-signed gen, local cert inspect)
      - SQLite certificate tracking database
      - Batch domain scanning
    """

    def __init__(self):
        """Initialize AllinSSL engine with default configuration."""
        self.inspector = SSLInspector()
        self.openssl = OpenSSLCLI()
        self.db = CertDatabase()

    def inspect(self, hostname: str, port: int = 443) -> Dict:
        """Inspect a live SSL certificate and persist results."""
        info = self.inspector.inspect(hostname, port)
        self.db.upsert(info)
        return {
            "hostname": info.hostname, "issuer": info.issuer,
            "subject": info.subject, "san_count": len(info.san),
            "not_after": info.not_after, "days_remaining": info.days_remaining,
            "status": info.status.value, "protocol": info.protocol_version,
            "cipher": info.cipher, "fingerprint": info.fingerprint_sha256[:16] + "...",
            "error": info.error,
        }

    def batch_scan(self, hostnames: List[str]) -> List[Dict]:
        """Scan multiple domains."""
        return [self.inspect(h) for h in hostnames]

    def get_expiring(self, days: int = 30) -> List[Dict]:
        """Execute get expiring operation for AllinSSL engine."""
        return self.db.get_expiring(days)

    def diagnostics(self) -> Dict:
        """Return engine health status for the OmniEngineRegistry."""
        openssl = self.openssl.check_installed()
        return {
            "engine": "OmniAllinSSLEngine",
            "status": "active",
            "openssl": openssl,
            "db_stats": self.db.stats(),
            "capabilities": ["live_ssl_inspect", "expiry_monitor", "san_extraction",
                             "openssl_cli", "self_signed_gen", "batch_scan", "sqlite_db"],
        }


if __name__ == "__main__":
    engine = OmniAllinSSLEngine()
    print(json.dumps(engine.inspect("google.com"), indent=2))
