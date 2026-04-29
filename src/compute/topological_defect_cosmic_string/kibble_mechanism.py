import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class KibbleMechanism:
    def __init__(self):
        pass

    def compute_string_tension(self, phase_transition_temp_gev: float) -> OmniResult:
        if phase_transition_temp_gev <= 0:
            return OmniResult(error="Temperature must be positive")

        # Deterministic calculation of Cosmic String Tension via the Kibble Mechanism.
        # Shortly after the Big Bang, as the universe cooled, the vacuum underwent phase transitions
        # (symmetry breaking). Sometimes, these transitions mismatched across different regions,
        # leaving behind 1D topological defects known as Cosmic Strings.
        # They are thinner than a proton but as heavy as a galaxy.
        try:
            # String tension (mu) is proportional to the square of the symmetry breaking energy scale.
            # mu ~ (energy_scale)^2
            
            tension_gev2 = phase_transition_temp_gev ** 2
            
            # Convert to physical tension (mass per unit length, kg/m)
            # 1 GeV^2 is roughly 10^20 kg/m
            tension_kg_per_meter = tension_gev2 * 1e20
            
            return OmniResult(value=tension_kg_per_meter)
        except Exception as e:
            return OmniResult(error=str(e))
