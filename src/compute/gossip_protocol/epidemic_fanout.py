import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class EpidemicMath:
    def __init__(self):
        pass

    def compute_infection_probability(self, rounds: int, fanout: int, total_nodes: int) -> OmniResult:
        if rounds < 0 or fanout <= 0 or total_nodes <= 0:
            return OmniResult(error="Invalid epidemic parameters")

        # Deterministic simulation of gossip protocol epidemic spread math
        # Probability that a specific node is infected after 'rounds'
        # Approx: 1 - (1 - 1/N)^(f^r) where f is fanout, r is rounds, N is nodes
        
        try:
            nodes_contacted = fanout ** rounds
            if nodes_contacted >= total_nodes * 10:
                # Prevent float overflow for massive powers
                prob = 1.0
            else:
                prob = 1.0 - math.pow((1.0 - 1.0/total_nodes), nodes_contacted)
            
            return OmniResult(value=prob)
        except Exception as e:
            return OmniResult(error=str(e))
