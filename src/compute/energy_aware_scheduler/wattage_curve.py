class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class WattageCurve:
    def __init__(self):
        pass

    def compute_energy_efficiency(self, token_throughput: float, wattage: float) -> OmniResult:
        if token_throughput < 0 or wattage <= 0:
            return OmniResult(error="Metrics must be positive")

        # Deterministic calculation of AI Energy Efficiency
        # Used by mobile/IoT edge devices to balance LLM generation speed against battery drain
        try:
            # Tokens per Joule (1 Watt = 1 Joule/second)
            # If we generate 10 tokens/sec at 5 Watts, efficiency is 2 tokens/Joule
            efficiency = token_throughput / wattage
            
            return OmniResult(value=efficiency)
        except Exception as e:
            return OmniResult(error=str(e))
