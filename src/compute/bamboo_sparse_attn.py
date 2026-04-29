# OMNI Compute Layer - Bamboo Sparse Attn
import numpy as np

class BambooError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def apply_powerinfer_sparsity(attention_scores: np.ndarray, threshold: float) -> Result:
    """Applies activation sparsity for Bamboo-7B PowerInfer execution."""
    try:
        if threshold < 0:
            return Result(error=BambooError("Threshold must be positive"))
            
        mask = attention_scores > threshold
        sparse_scores = attention_scores * mask
        
        density = float(np.sum(mask) / attention_scores.size)
        return Result(value={"sparse_matrix": sparse_scores, "density": density})
    except Exception as e:
        return Result(error=BambooError(f"Sparsity application failed: {str(e)}"))
