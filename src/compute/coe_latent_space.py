# OMNI Compute Layer - Chain of Embedding (Latent Space)
import numpy as np

class CoEError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def compute_latent_chain_shift(embeddings: np.ndarray) -> Result:
    """Computes Chain-of-Embedding latent shifts for Self-Evaluation."""
    try:
        if len(embeddings.shape) != 2 or embeddings.shape[0] < 2:
            return Result(error=CoEError("Embeddings must be a 2D array with at least 2 steps"))
            
        shifts = np.diff(embeddings, axis=0)
        magnitudes = np.linalg.norm(shifts, axis=1)
        
        # Calculate latent convergence
        convergence_score = float(np.mean(magnitudes[-2:]) / (np.mean(magnitudes[:2]) + 1e-6))
        
        return Result(value={"shifts": shifts, "convergence": convergence_score})
    except Exception as e:
        return Result(error=CoEError(f"Latent calculation failed: {str(e)}"))
