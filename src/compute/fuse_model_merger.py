# OMNI Compute Layer - Fuse Model Merger
import numpy as np

class FuseError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def slerp_weights(w1: np.ndarray, w2: np.ndarray, t: float) -> Result:
    """Spherical Linear Interpolation for model fusion."""
    try:
        if w1.shape != w2.shape:
            return Result(error=FuseError("Weight shapes must match"))
            
        w1_norm = w1 / (np.linalg.norm(w1) + 1e-8)
        w2_norm = w2 / (np.linalg.norm(w2) + 1e-8)
        
        omega = np.arccos(np.clip(np.dot(w1_norm.flatten(), w2_norm.flatten()), -1.0, 1.0))
        so = np.sin(omega)
        
        if so == 0:
            merged = (1.0 - t) * w1 + t * w2
        else:
            merged = (np.sin((1.0 - t) * omega) / so) * w1 + (np.sin(t * omega) / so) * w2
            
        return Result(value={"merged_weights": merged})
    except Exception as e:
        return Result(error=FuseError(f"Fusion failed: {str(e)}"))
