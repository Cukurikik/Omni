import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class BoseEinsteinCondensate:
    def __init__(self):
        pass

    def compute_thermal_noise_entropy(self, temperature_kelvin: float) -> OmniResult:
        if temperature_kelvin < 0:
            return OmniResult(error="Invalid temperature (below absolute zero)")

        # Deterministic calculation of Absolute Zero Entropy Crystal stability.
        # To store data permanently without ANY degradation, it must be stored in a 
        # perfect crystal lattice at Absolute Zero (0 Kelvin), where entropy is zero
        # (Third Law of Thermodynamics).
        try:
            # Below a critical temperature, particles form a Bose-Einstein Condensate,
            # acting as a single quantum entity with zero electrical resistance and zero friction.
            
            # Simplified entropy calculation based on temperature approaching zero
            # S -> 0 as T -> 0
            
            if temperature_kelvin == 0.0:
               return OmniResult(value=0.0) # Perfect zero entropy
               
            # E = kT ln(W) approximation
            entropy_j_k = 1.38e-23 * temperature_kelvin * math.log(temperature_kelvin + 1.0)
            
            return OmniResult(value=entropy_j_k)
        except Exception as e:
            return OmniResult(error=str(e))
