import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class CoherenceDecay:
    def __init__(self):
        pass

    def compute_fidelity_decay(self, time_elapsed_us: float, t1_relaxation_time_us: float, t2_dephasing_time_us: float) -> OmniResult:
        if t1_relaxation_time_us <= 0 or t2_dephasing_time_us <= 0 or time_elapsed_us < 0:
            return OmniResult(error="Times must be positive")

        # Deterministic calculation of Quantum Qubit Coherence Loss.
        # Quantum computers lose their data incredibly fast due to interaction with the environment.
        # T1 is how fast a qubit flips from |1> back to |0> (energy relaxation).
        # T2 is how fast a qubit loses its phase relationship (dephasing).
        try:
            # Fidelity roughly decays exponentially based on T1 and T2
            # Simplified deterministic mock of the combined decay envelope
            
            t1_decay = math.exp(-time_elapsed_us / t1_relaxation_time_us)
            t2_decay = math.exp(-time_elapsed_us / t2_dephasing_time_us)
            
            # Overall quantum state fidelity
            fidelity = t1_decay * t2_decay
            
            return OmniResult(value=fidelity)
        except Exception as e:
            return OmniResult(error=str(e))
