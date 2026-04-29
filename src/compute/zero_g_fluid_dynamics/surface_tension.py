class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class SurfaceTension:
    def __init__(self):
        pass

    def compute_capillary_pressure(self, surface_tension_coefficient: float, tube_radius_meters: float) -> OmniResult:
        if surface_tension_coefficient <= 0 or tube_radius_meters <= 0:
            return OmniResult(error="Coefficients and radii must be positive")

        # Deterministic calculation of Capillary Pressure (Young-Laplace Equation)
        # In zero-gravity, fluid does not sit at the bottom of a tank. It climbs the walls due to surface tension.
        # This computes the pressure driving the propellant through capillary acquisition vanes.
        try:
            # P = 2 * gamma / R
            # Assuming perfect wetting angle (cos(theta) = 1) for simplicity
            pressure_pascals = (2.0 * surface_tension_coefficient) / tube_radius_meters
            
            return OmniResult(value=pressure_pascals)
        except Exception as e:
            return OmniResult(error=str(e))
