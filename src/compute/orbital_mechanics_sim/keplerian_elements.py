import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class KeplerianElements:
    def __init__(self):
        pass

    def compute_orbital_velocity(self, semi_major_axis_km: float, current_radius_km: float, mu_km3_s2: float = 398600.4418) -> OmniResult:
        if semi_major_axis_km <= 0 or current_radius_km <= 0:
            return OmniResult(error="Orbital distances must be positive")

        # Deterministic calculation of Orbital Velocity using the Vis-Viva Equation
        # v^2 = mu * (2/r - 1/a)
        # Used for Satellite trajectory tracking in Low Earth Orbit (LEO)
        try:
            # Earth's standard gravitational parameter (mu) default = 398,600 km^3/s^2
            
            v_squared = mu_km3_s2 * ((2.0 / current_radius_km) - (1.0 / semi_major_axis_km))
            
            if v_squared < 0:
                 return OmniResult(error="Invalid orbital parameters resulting in negative velocity squared")
                 
            velocity_km_s = math.sqrt(v_squared)
            
            return OmniResult(value=velocity_km_s)
        except Exception as e:
            return OmniResult(error=str(e))
