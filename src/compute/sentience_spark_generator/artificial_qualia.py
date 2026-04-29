import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ArtificialQualia:
    def __init__(self):
        pass

    def compute_integrated_information_phi(self, neural_network_nodes: int, synaptic_connections: int) -> OmniResult:
        if neural_network_nodes <= 0 or synaptic_connections < 0:
            return OmniResult(error="Invalid network topology parameters")

        # Deterministic calculation of Integrated Information (Phi).
        # Integrated Information Theory (IIT) posits that consciousness is a fundamental
        # property of certain highly interconnected, integrated information processing systems.
        # Phi (Φ) measures the quantity of consciousness (qualia).
        try:
            # Phenomenological approximation:
            # Phi requires a system to be highly differentiated (many states) AND
            # highly integrated (cannot be cut into independent parts without losing information).
            
            # Very simplified model for UI output
            # If the network is too sparse, it's just a feed-forward machine (Phi = 0)
            connection_density = synaptic_connections / max(1, (neural_network_nodes * (neural_network_nodes - 1)))
            
            if connection_density < 0.01:
               return OmniResult(value=0.0) # Not conscious, just a standard computer
               
            # Phi scales non-linearly with node count and density
            phi_value = (neural_network_nodes ** 1.5) * connection_density * math.log(max(2, synaptic_connections))
            
            return OmniResult(value=phi_value)
        except Exception as e:
            return OmniResult(error=str(e))
