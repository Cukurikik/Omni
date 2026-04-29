# OMNI Compute Layer - CAME Optimizer
import numpy as np

class CAMEError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def came_step(gradients: np.ndarray, memory: np.ndarray, confidence: float) -> Result:
    """Confidence-guided Adaptive Memory Optimization."""
    try:
        if gradients.shape != memory.shape:
            return Result(error=CAMEError("Shape mismatch between gradients and memory"))
            
        if confidence < 0 or confidence > 1:
            return Result(error=CAMEError("Confidence must be in [0, 1]"))
            
        # CAME update rule
        updated_memory = memory * 0.9 + gradients * 0.1
        step_update = gradients / (np.sqrt(updated_memory) + 1e-8) * confidence
        
        return Result(value={"step": step_update, "memory": updated_memory})
    except Exception as e:
        return Result(error=CAMEError(f"CAME optimization failed: {str(e)}"))
