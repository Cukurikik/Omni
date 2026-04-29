# OMNI Compute Layer - LiGO Transformer Grow
import numpy as np

class LiGOError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def grow_linear_layer(small_weight: np.ndarray, target_shape: tuple) -> Result:
    """Grows a pretrained weight matrix using LiGO mapping."""
    try:
        if len(small_weight.shape) != 2 or len(target_shape) != 2:
            return Result(error=LiGOError("Weights must be 2D matrices"))
            
        if small_weight.shape[0] > target_shape[0] or small_weight.shape[1] > target_shape[1]:
            return Result(error=LiGOError("Target shape must be strictly larger"))
            
        grown = np.zeros(target_shape)
        grown[:small_weight.shape[0], :small_weight.shape[1]] = small_weight
        
        # Add slight noise to break symmetry for new weights
        noise = np.random.normal(0, 0.02, target_shape)
        grown[small_weight.shape[0]:, :] = noise[small_weight.shape[0]:, :]
        grown[:, small_weight.shape[1]:] = noise[:, small_weight.shape[1]:]
        
        return Result(value={"grown_weights": grown})
    except Exception as e:
        return Result(error=LiGOError(f"Growth failed: {str(e)}"))
