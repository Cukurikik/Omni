class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class LatencyOptimizer:
    def __init__(self):
        pass

    def calculate_routing_cost(self, latency_ms: float, bandwidth_mbps: float, server_load_pct: float) -> OmniResult:
        if latency_ms < 0 or bandwidth_mbps <= 0 or server_load_pct < 0 or server_load_pct > 100:
            return OmniResult(error="Invalid routing metrics")

        # Deterministic calculation of Edge Node routing costs
        # Used to dynamically route AI requests to the absolute fastest Edge node available
        try:
            # Heuristic cost function: higher is worse
            # Penalizes high latency heavily, penalizes overloaded servers
            load_factor = 1.0 + (server_load_pct / 100.0)**2
            latency_factor = latency_ms * 2.0
            bandwidth_factor = 1000.0 / bandwidth_mbps
            
            total_cost = (latency_factor + bandwidth_factor) * load_factor
            
            return OmniResult(value=total_cost)
        except Exception as e:
            return OmniResult(error=str(e))
