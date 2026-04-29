import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class AsymmetricRadiation:
    def __init__(self):
        pass

    def compute_stellar_thrust(self, stellar_luminosity_watts: float, mirror_coverage_angle_radians: float) -> OmniResult:
        if stellar_luminosity_watts <= 0 or mirror_coverage_angle_radians <= 0 or mirror_coverage_angle_radians > 2 * math.pi:
            return OmniResult(error="Invalid Shkadov thruster parameters")

        # Deterministic calculation of Shkadov Thruster output.
        # A Shkadov thruster is a massive semi-circular mirror placed on one side of a star.
        # It reflects radiation back, creating an asymmetric radiation pressure that slowly
        # pushes the entire star (and its planets) through the galaxy.
        try:
            c = 299792458.0 # Speed of light
            
            # Total radiation pressure force = L / c
            # But the mirror only covers a portion of the star, and is angled.
            # A perfect hemispherical mirror (pi radians) gives a thrust of ~ L / 2c
            
            # Simplified force equation integrating over the solid angle of the mirror
            thrust_newtons = (stellar_luminosity_watts / c) * (1.0 - math.cos(mirror_coverage_angle_radians / 2.0))
            
            return OmniResult(value=thrust_newtons)
        except Exception as e:
            return OmniResult(error=str(e))
