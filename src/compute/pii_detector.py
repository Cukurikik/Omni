# OMNI Compute Layer - PII Detector
import re

class PIIError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def detect_pii(text: str) -> Result:
    """Detects PII in logs for GDPR compliance."""
    try:
        if not text:
            return Result(error=PIIError("Empty text for PII detection"))
            
        # Basic patterns for email and SSN
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        
        emails = re.findall(email_pattern, text)
        ssns = re.findall(ssn_pattern, text)
        
        has_pii = len(emails) > 0 or len(ssns) > 0
        return Result(value={"has_pii": has_pii, "emails_count": len(emails), "ssns_count": len(ssns)})
    except Exception as e:
        return Result(error=PIIError(f"Detection failed: {str(e)}"))
