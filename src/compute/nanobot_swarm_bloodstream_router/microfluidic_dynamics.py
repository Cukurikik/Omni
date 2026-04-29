import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MicrofluidicDynamics:
    def __init__(self):
        pass

    def compute_drag_force(self, radius_meters: float, velocity_m_s: float, dynamic_viscosity_pa_s: float) -> OmniResult:
        if radius_meters <= 0 or dynamic_viscosity_pa_s <= 0:
            return OmniResult(error="Physical parameters must be positive")

        # Deterministic calculation of Stokes' Law for Nanobot Bloodstream Navigation
        # At the microscopic scale inside a human blood vessel, inertia is irrelevant (low Reynolds number).
        # Nanobots must constantly fight extreme viscous drag, swimming through blood like it's thick honey.
        try:
            # F_d = 6 * pi * viscosity * radius * velocity
            drag_force_newtons = 6.0 * math.pi * dynamic_viscosity_pa_s * radius_meters * velocity_m_s
            
            return OmniResult(value=drag_force_newtons)
        except Exception as e:
            return OmniResult(error=str(e))
