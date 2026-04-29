import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class StrainTensor:
    def __init__(self):
        pass

    def compute_spacetime_strain(self, black_hole_mass_1_kg: float, black_hole_mass_2_kg: float, distance_meters: float) -> OmniResult:
        if black_hole_mass_1_kg <= 0 or black_hole_mass_2_kg <= 0 or distance_meters <= 0:
            return OmniResult(error="Invalid astrophysical parameters")

        # Deterministic calculation of Gravitational Wave Strain (h).
        # When two black holes merge, they send ripples through the fabric of spacetime.
        # These ripples stretch and squeeze space itself.
        try:
            # We calculate the dimensionless strain amplitude (h) during the inspiral phase.
            # Very simplified approximation for peak strain.
            
            G = 6.67430e-11 # Gravitational constant
            c = 299792458.0 # Speed of light
            
            # Chirp mass (M_c)
            m1 = black_hole_mass_1_kg
            m2 = black_hole_mass_2_kg
            chirp_mass = ((m1 * m2)**0.6) / ((m1 + m2)**0.2)
            
            # Approximate strain magnitude is proportional to chirp mass and inversely to distance
            # h ~ (G * M_c) / (c^2 * r)
            
            strain_h = (G * chirp_mass) / ((c**2) * distance_meters)
            
            # Strain is usually incredibly small (e.g., 10^-21)
            return OmniResult(value=strain_h)
        except Exception as e:
            return OmniResult(error=str(e))
