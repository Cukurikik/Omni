import hmac
import hashlib

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class HMACCrypto:
    def __init__(self):
        pass

    def compute_sha256_signature(self, header_b64: str, payload_b64: str, secret: str) -> OmniResult:
        if not header_b64 or not payload_b64 or not secret:
            return OmniResult(error="Header, Payload, and Secret must not be empty")

        # Deterministic HMAC-SHA256 mathematical calculation for JWT Integrity
        try:
            signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
            key = secret.encode('utf-8')
            
            signature = hmac.new(key, signing_input, hashlib.sha256).digest()
            
            return OmniResult(value=signature)
        except Exception as e:
            return OmniResult(error=str(e))
