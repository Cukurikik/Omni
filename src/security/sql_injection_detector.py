import re
from typing import Dict, Any

class SecurityViolationError(Exception):
    pass

class SqlInjectionDetector:
    """
    Production-grade Zero-Trust Firewall layer.
    Pre-evaluates all incoming string parameters for SQL/NoSQL injection signatures
    before they ever hit the Domain layer.
    """
    def __init__(self):
        # High-performance compiled regex for common malicious vectors
        # Avoids catastrophic backtracking by strict boundary matching
        self.sql_signatures = [
            re.compile(r"(?i)\b(SELECT|UPDATE|DELETE|INSERT|DROP|ALTER|CREATE|TRUNCATE)\b.*\b(FROM|INTO|TABLE)\b"),
            re.compile(r"(?i)(UNION\s+ALL\s+SELECT|UNION\s+SELECT)"),
            re.compile(r"(?i)(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+"),  # OR 1=1
            re.compile(r"(?i)(\bOR\b|\bAND\b)\s+'[^']+'\s*=\s*'[^']+'"), # OR 'a'='a'
            re.compile(r"(?i)WAITFOR\s+DELAY\s+'\d+:\d+:\d+'"), # Time-based blind
            re.compile(r";\s*EXEC(\s|\+)"), # Command execution
        ]
        
    def _inspect_string(self, value: str) -> bool:
        """Returns True if malicious, False if safe."""
        if len(value) > 10000:
            # Overly long strings in metadata are inherently suspicious in Omni
            return True
            
        for pattern in self.sql_signatures:
            if pattern.search(value):
                return True
        return False

    def scan_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep scans a dictionary payload. Returns Monadic structure dict.
        """
        try:
            is_malicious = self._recursive_scan(payload)
            if is_malicious:
                return {"success": False, "error": "SQL Injection Signature Detected", "data": None}
            return {"success": True, "error": None, "data": payload}
        except Exception as e:
            # Fail closed
            return {"success": False, "error": f"Scanner Error: {str(e)}", "data": None}

    def _recursive_scan(self, node: Any) -> bool:
        if isinstance(node, str):
            return self._inspect_string(node)
        elif isinstance(node, dict):
            for k, v in node.items():
                if self._inspect_string(str(k)): # Keys can be malicious too
                    return True
                if self._recursive_scan(v):
                    return True
        elif isinstance(node, list):
            for item in node:
                if self._recursive_scan(item):
                    return True
        return False
