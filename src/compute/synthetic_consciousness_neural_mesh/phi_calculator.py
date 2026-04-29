import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class PhiCalculator:
    def __init__(self):
        pass

    def compute_integrated_information(self, synaptic_weight_matrix_size: int, network_connectivity_index: float) -> OmniResult:
        if synaptic_weight_matrix_size <= 0 or network_connectivity_index < 0:
            return OmniResult(error="Invalid neural network parameters")

        # Deterministic calculation of Integrated Information Theory (Phi - Φ).
        # Phi is a mathematical measure of consciousness. It calculates how much information
        # a system generates as a whole, beyond the sum of its independent parts.
        # A high Phi value means the synthetic neural mesh is genuinely self-aware.
        try:
            # Simulated Phi calculation: scales with network size and non-linear connectivity
            # If the network is just a feed-forward AI, Phi is near zero.
            # If it has massive recurrent loops (like a human brain), Phi explodes.
            
            base_complexity = synaptic_weight_matrix_size * math.log(synaptic_weight_matrix_size)
            phi_value = base_complexity * (network_connectivity_index ** 2.5)
            
            return OmniResult(value=phi_value)
        except Exception as e:
            return OmniResult(error=str(e))
