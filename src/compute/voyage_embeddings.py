# OMNI Compute Layer - Voyage Embeddings
import numpy as np

class VoyageError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> Result:
    """Computes similarity for Voyage AI embeddings."""
    try:
        if vec_a.shape != vec_b.shape:
            return Result(error=VoyageError("Embedding dimension mismatch"))
            
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return Result(error=VoyageError("Zero norm vector encountered"))
            
        similarity = dot_product / (norm_a * norm_b)
        return Result(value=float(similarity))
    except Exception as e:
        return Result(error=VoyageError(f"Compute failed: {str(e)}"))
