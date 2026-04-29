class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class OverprovisionAnomaly:
    def __init__(self):
        pass

    def detect_waste(self, cpu_utilization_percent: float, memory_utilization_percent: float, hourly_cost: float) -> OmniResult:
        if cpu_utilization_percent < 0 or memory_utilization_percent < 0 or hourly_cost <= 0:
            return OmniResult(error="Invalid telemetry metrics")

        # Deterministic calculation of Cloud Resource Over-provisioning (Waste)
        # Identifies massive EC2/GCE instances that are sitting idle, burning cash
        try:
            # If both CPU and RAM are under 10% utilization for the period, it's an anomaly
            is_wasted = cpu_utilization_percent < 10.0 and memory_utilization_percent < 10.0
            
            # Calculate wasted spend
            wasted_dollars = hourly_cost if is_wasted else 0.0
            
            return OmniResult(value={"is_anomaly": is_wasted, "wasted_hourly_spend": wasted_dollars})
        except Exception as e:
            return OmniResult(error=str(e))
