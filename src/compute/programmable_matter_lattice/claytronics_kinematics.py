import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ClaytronicsKinematics:
    def __init__(self):
        pass

    def compute_voxel_displacement(self, current_x: float, current_y: float, target_x: float, target_y: float) -> OmniResult:
        # Deterministic calculation of Claytronics Shape-Shifting Kinematics.
        # Programmable matter (utility fog or claytronics) consists of billions of microscopic
        # robots (catoms) that roll over each other using electrostatic forces to form any 3D object.
        try:
            # Calculate Euclidean distance the nanobot must travel
            dx = target_x - current_x
            dy = target_y - current_y
            
            distance = math.sqrt(dx**2 + dy**2)
            
            return OmniResult(value=distance)
        except Exception as e:
            return OmniResult(error=str(e))
