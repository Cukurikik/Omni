class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ChaCha20Math:
    def __init__(self):
        pass

    def compute_quarter_round(self, a: int, b: int, c: int, d: int) -> OmniResult:
        # Deterministic ChaCha20 quarter round math for WireGuard core cryptography
        # Operates on 32-bit unsigned integers
        
        def rotl32(v, c):
            return ((v << c) & 0xFFFFFFFF) | (v >> (32 - c))

        try:
            # First half
            a = (a + b) & 0xFFFFFFFF
            d ^= a
            d = rotl32(d, 16)

            c = (c + d) & 0xFFFFFFFF
            b ^= c
            b = rotl32(b, 12)

            # Second half
            a = (a + b) & 0xFFFFFFFF
            d ^= a
            d = rotl32(d, 8)

            c = (c + d) & 0xFFFFFFFF
            b ^= c
            b = rotl32(b, 7)

            return OmniResult(value=(a, b, c, d))
        except Exception as e:
            return OmniResult(error=str(e))
