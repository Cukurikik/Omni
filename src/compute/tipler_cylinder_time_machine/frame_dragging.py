import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class FrameDragging:
    def __init__(self):
        pass

    def compute_closed_timelike_curve_radius(self, cylinder_mass_kg: float, angular_velocity_rad_s: float) -> OmniResult:
        if cylinder_mass_kg <= 0 or angular_velocity_rad_s <= 0:
            return OmniResult(error="Invalid Tipler Cylinder parameters")

        # Deterministic calculation of Tipler Cylinder Frame-Dragging.
        # A Tipler Cylinder is an infinitely long, incredibly dense cylinder spinning
        # near the speed of light. Due to General Relativity, it drags the fabric of
        # spacetime along with it (frame-dragging). If you fly a ship around it in the
        # right trajectory, you can travel backwards in time along a Closed Timelike Curve (CTC).
        try:
            G = 6.67430e-11 # Gravitational constant
            c = 299792458.0 # Speed of light
            
            # This is a highly simplified phenomenological approximation of the Van Stockum dust metric
            # To create a CTC, the rotational frame-dragging must exceed the speed of light.
            # R_ctc ~ (G * M * w) / c^3
            
            ctc_radius_meters = (G * cylinder_mass_kg * angular_velocity_rad_s) / (c**3)
            
            return OmniResult(value=ctc_radius_meters)
        except Exception as e:
            return OmniResult(error=str(e))
