class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MurmurMath:
    def __init__(self):
        pass

    def compute_avalanche_mixing(self, h: int) -> OmniResult:
        if h < 0:
            return OmniResult(error="Input hash state must be non-negative")

        # Deterministic MurmurHash3 32-bit final avalanche mixing (fmix32)
        try:
            h ^= h >> 16
            h = (h * 0x85ebca6b) & 0xFFFFFFFF
            h ^= h >> 13
            h = (h * 0xc2b2ae35) & 0xFFFFFFFF
            h ^= h >> 16
            
            return OmniResult(value=h)
        except Exception as e:
            return OmniResult(error=str(e))
