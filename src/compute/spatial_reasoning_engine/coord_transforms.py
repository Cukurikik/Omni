class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class CoordTransforms:
    def __init__(self):
        pass

    def compute_3d_distance(self, p1: list, p2: list) -> OmniResult:
        if len(p1) != 3 or len(p2) != 3:
            return OmniResult(error="Points must be 3-dimensional [x, y, z]")

        # Deterministic simulation of Spatial reasoning coordinates
        # Used by LLMs to answer questions like "Is the mug inside the microwave?"
        try:
            import math
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            dz = p1[2] - p2[2]
            
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            return OmniResult(value=dist)
        except Exception as e:
            return OmniResult(error=str(e))
