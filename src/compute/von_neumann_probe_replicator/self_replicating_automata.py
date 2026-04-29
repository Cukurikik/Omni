import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SelfReplicatingAutomata:
    def __init__(self):
        pass

    def compute_exponential_growth_time(self, initial_probes: int, target_probes: int, generation_time_days: float) -> OmniResult:
        if initial_probes <= 0 or target_probes <= 0 or generation_time_days <= 0:
            return OmniResult(error="Invalid von Neumann replication parameters")

        # Deterministic calculation of Von Neumann Probe replication times.
        # A von Neumann probe is an autonomous spacecraft that travels to a star system,
        # mines asteroids, and builds copies of itself. This leads to exponential growth,
        # allowing us to explore the entire galaxy in a few million years.
        try:
            # Formula: P(t) = P_0 * 2^(t / T_g)
            # We want to solve for t (time required)
            # t = T_g * log2(P_t / P_0)
            
            ratio = float(target_probes) / float(initial_probes)
            
            if ratio <= 1.0:
                return OmniResult(value=0.0)
                
            time_required_days = generation_time_days * math.log2(ratio)
            time_required_years = time_required_days / 365.25
            
            return OmniResult(value=time_required_years)
        except Exception as e:
            return OmniResult(error=str(e))
