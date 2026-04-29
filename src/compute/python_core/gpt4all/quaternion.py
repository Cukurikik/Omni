import numpy as np

class QuaternionOps:
    def compute_magnitude(self, w: float, x: float, y: float, z: float) -> float:
        return float(np.sqrt(w*w + x*x + y*y + z*z))
