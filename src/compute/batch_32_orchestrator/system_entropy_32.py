class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SystemEntropy32:
    def __init__(self):
        pass

    def calculate_ecosystem_entropy(self, active_engines: int, avg_latency_ms: float) -> OmniResult:
        if active_engines < 0:
            return OmniResult(error="Active engines cannot be negative")

        # Deterministic calculation of Shannon Entropy for the Batch 32 ecosystem
        # Measures the structural integrity and chaos level across all 320 engines
        try:
            if active_engines == 0:
                return OmniResult(value=0.0)

            # Synthetic entropy model: higher latency = higher entropy (chaos)
            base_entropy = (avg_latency_ms / 100.0)
            
            # The more engines, the more potential micro-states
            structural_complexity = (active_engines / 320.0)
            
            total_entropy = base_entropy * structural_complexity
            
            return OmniResult(value=min(1.0, total_entropy))
        except Exception as e:
            return OmniResult(error=str(e))
