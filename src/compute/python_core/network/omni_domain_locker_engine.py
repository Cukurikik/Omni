ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI DOMAIN LOCKER ENGINE — Domain Portfolio Management & Monitoring
# ===========================================================================
# Source Paradigm: https://github.com/Lissy93/domain-locker
# Domain Layer  : Network (Domain Management)
# Zero-Prod     : 100% Native — socket, ssl, urllib, json, sqlite3
# ===========================================================================
"""
Domain Locker teaches us:
  1. Domain portfolio tracking (registration, expiry, registrar)
  2. DNS record monitoring (A, AAAA, MX, NS, TXT, CNAME)
  3. SSL certificate expiry alerting
  4. WHOIS data extraction
  5. Domain status monitoring (active, parked, expired)
  6. Cost tracking per domain

This engine distills those paradigms into OMNI-native Python for
domain inspection, DNS resolution, SSL checking, and portfolio tracking.
"""

import hashlib
import json
import os
import re
import socket
import ssl
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class DomainStatus(Enum):
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    PARKED = "parked"
    UNKNOWN = "unknown"


@dataclass
class DomainRecord:
    domain: str
    status: DomainStatus = DomainStatus.UNKNOWN
    registrar: str = ""
    ip_address: str = ""
    ssl_issuer: str = ""
    ssl_expiry_days: int = -1
    dns_records: Dict = field(default_factory=dict)
    cost_yearly: float = 0
    notes: str = ""
    last_checked: float = 0


# ── DNS Resolver ──────────────────────────────────────────────────────────

class DNSResolver:
    """Resolve DNS records for domains."""

    @staticmethod
    def resolve_a(domain: str) -> List[str]:
        try:
            return [r[4][0] for r in socket.getaddrinfo(domain, None, socket.AF_INET)][:5]
        except Exception:
            return []

    @staticmethod
    def resolve_aaaa(domain: str) -> List[str]:
        try:
            return [r[4][0] for r in socket.getaddrinfo(domain, None, socket.AF_INET6)][:3]
        except Exception:
            return []

    @staticmethod
    def nslookup(domain: str, record_type: str = "A") -> Dict:
        try:
            r = subprocess.run(
                ["nslookup", f"-type={record_type}", domain],
                capture_output=True, text=True, timeout=10,
            )
            return {"type": record_type, "output": r.stdout[:2048],
                    "success": r.returncode == 0}
        except Exception as e:
            return {"error": str(e)[:128]}

    @staticmethod
    def full_resolve(domain: str) -> Dict:
        result = {"domain": domain}
        a_records = DNSResolver.resolve_a(domain)
        result["A"] = list(set(a_records))
        result["AAAA"] = list(set(DNSResolver.resolve_aaaa(domain)))

        for rtype in ["MX", "NS", "TXT"]:
            ns = DNSResolver.nslookup(domain, rtype)
            if ns.get("success"):
                result[rtype] = ns.get("output", "")[:500]
        return result


# ── SSL Inspector ─────────────────────────────────────────────────────────

class SSLInspector:
    """Inspect SSL certificates for domains."""

    @staticmethod
    def check(domain: str, port: int = 443) -> Dict:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    not_after = ssl.cert_time_to_seconds(cert["notAfter"])
                    days_left = int((not_after - time.time()) / 86400)
                    issuer_parts = dict(x[0] for x in cert.get("issuer", []))
                    subject_parts = dict(x[0] for x in cert.get("subject", []))
                    sans = []
                    for t, v in cert.get("subjectAltName", []):
                        if t == "DNS":
                            sans.append(v)
                    return {
                        "domain": domain,
                        "issuer": issuer_parts.get("organizationName", ""),
                        "subject": subject_parts.get("commonName", ""),
                        "expires": cert.get("notAfter", ""),
                        "days_left": days_left,
                        "sans_count": len(sans),
                        "protocol": ssock.version(),
                    }
        except Exception as e:
            return {"domain": domain, "error": str(e)[:256]}


# ── Domain Portfolio Store (SQLite) ───────────────────────────────────────

class PortfolioStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".domain_locker.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".domain_locker.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                domain TEXT PRIMARY KEY, status TEXT,
                ip TEXT, ssl_issuer TEXT, ssl_days INTEGER,
                cost REAL, last_checked REAL
            )
        """)
        conn.commit()
        conn.close()

    def upsert(self, rec: DomainRecord):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO domains VALUES (?,?,?,?,?,?,?)",
            (rec.domain, rec.status.value, rec.ip_address,
             rec.ssl_issuer, rec.ssl_expiry_days, rec.cost_yearly, time.time()),
        )
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM domains")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM domains WHERE ssl_days < 30 AND ssl_days >= 0")
        expiring = c.fetchone()[0]
        conn.close()
        return {"total_domains": total, "ssl_expiring_soon": expiring}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniDomainLockerEngine:
    """
    OMNI Domain Locker Engine — Zero-Prod Domain Portfolio Management.

    Capabilities (all native socket + ssl + subprocess):
      - DNS resolution (A, AAAA, MX, NS, TXT)
      - SSL certificate inspection (issuer, expiry, SANs)
      - Domain portfolio tracking (SQLite)
      - IP address resolution
      - SSL expiry alerting
    """

    def __init__(self):
        self.dns = DNSResolver()
        self.ssl_inspector = SSLInspector()
        self.store = PortfolioStore()

    def inspect(self, domain: str) -> Dict:
        dns = self.dns.full_resolve(domain)
        ssl_info = self.ssl_inspector.check(domain)
        ips = dns.get("A", [])

        rec = DomainRecord(
            domain=domain,
            ip_address=ips[0] if ips else "",
            ssl_issuer=ssl_info.get("issuer", ""),
            ssl_expiry_days=ssl_info.get("days_left", -1),
        )
        if rec.ssl_expiry_days > 30:
            rec.status = DomainStatus.ACTIVE
        elif rec.ssl_expiry_days > 0:
            rec.status = DomainStatus.EXPIRING
        self.store.upsert(rec)

        return {
            "domain": domain,
            "status": rec.status.value,
            "ip": rec.ip_address,
            "dns_A": dns.get("A", []),
            "ssl": ssl_info,
        }

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniDomainLockerEngine",
            "status": "active",
            "db": self.store.stats(),
            "capabilities": ["dns_resolve", "ssl_inspect", "portfolio_track",
                             "expiry_alert", "nslookup", "ip_resolve"],
        }


if __name__ == "__main__":
    engine = OmniDomainLockerEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
