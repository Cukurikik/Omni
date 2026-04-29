# hackingBuddyGPT — Vulnerability Scanner Pipeline
from typing import Optional, Generic, TypeVar, List, Dict
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class VulnScanner:
    MAX_PORTS = 65535; VULN_CATEGORIES = ["SQL_INJECTION", "XSS", "SSRF", "RCE", "LFI", "IDOR"]
    def scan_port_range(self, start: int, end: int) -> OmniResult[List[int], str]:
        if start < 1 or end > self.MAX_PORTS: return OmniResult(error="Port range invalid")
        if start > end: return OmniResult(error="Start > end")
        return OmniResult(value=list(range(start, end + 1)))

    def classify_finding(self, description: str, severity: float) -> OmniResult[Dict, str]:
        if not description: return OmniResult(error="Empty description")
        if severity < 0 or severity > 10: return OmniResult(error="Severity must be [0,10]")
        return OmniResult(value={"description": description[:500], "severity": severity, "critical": severity >= 9.0})
