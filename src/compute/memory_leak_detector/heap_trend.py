class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class HeapTrendAnalysis:
    def __init__(self):
        pass

    def compute_memory_growth_rate(self, memory_snapshots_mb: list) -> OmniResult:
        if len(memory_snapshots_mb) < 2:
            return OmniResult(error="Need at least two snapshots to calculate trend")

        # Deterministic calculation of memory heap growth rates
        # Used by the Memory Leak Detector agent to spot slow continuous allocations over time
        try:
            # Simple linear regression slope (growth rate per snapshot)
            n = len(memory_snapshots_mb)
            sum_x = sum(range(n))
            sum_y = sum(memory_snapshots_mb)
            sum_xy = sum(i * y for i, y in enumerate(memory_snapshots_mb))
            sum_xx = sum(i * i for i in range(n))
            
            denominator = n * sum_xx - sum_x * sum_x
            if denominator == 0:
                return OmniResult(value=0.0) # Flat
                
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            
            return OmniResult(value=slope) # MB per snapshot
        except Exception as e:
            return OmniResult(error=str(e))
