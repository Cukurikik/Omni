class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class EntropyMath:
    def __init__(self):
        pass

    def compute_shannon_entropy(self, engine_statuses: list[int]) -> OmniResult:
        if not engine_statuses:
            return OmniResult(error="Engine status array cannot be empty")

        # Deterministic calculation of Shannon entropy to measure system chaos
        # status codes: 0=Healthy, 1=Degraded, 2=Offline
        try:
            total = len(engine_statuses)
            counts = {0: 0, 1: 0, 2: 0}
            
            for s in engine_statuses:
                if s in counts:
                    counts[s] += 1
                    
            entropy = 0.0
            import math
            for k, v in counts.items():
                if v > 0:
                    p = v / total
                    entropy -= p * math.log2(p)
                    
            return OmniResult(value=entropy)
        except Exception as e:
            return OmniResult(error=str(e))
