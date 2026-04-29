# OMNI Compute Layer - LoRA Weight Fusion
import numpy as np

class LoraError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def compute_lora_delta(w_down: np.ndarray, w_up: np.ndarray, alpha: float, rank: int) -> Result:
    """Computes the exact weight delta for Low-Rank Adaptation."""
    try:
        if w_down.shape[1] != rank or w_up.shape[0] != rank:
            return Result(error=LoraError("Rank dimension mismatch"))
            
        scaling = alpha / rank
        delta = np.dot(w_up, w_down) * scaling
        
        return Result(value={"delta_weight": delta})
    except Exception as e:
        return Result(error=LoraError(f"Delta compute failed: {str(e)}"))
