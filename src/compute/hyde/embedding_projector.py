import numpy as np
from typing import Any

class OmniResult:
    def __init__(self, value: Any, error: str = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class EmbeddingProjector:
    def project(self, emb: np.ndarray, projection_matrix: np.ndarray) -> OmniResult:
        if emb is None or projection_matrix is None:
            return OmniResult(None, "Missing tensors")
            
        try:
            # Python matrix multiplication for HyDE embedding projection
            projected = np.dot(emb, projection_matrix)
            
            return OmniResult(projected)
        except Exception as e:
            return OmniResult(None, str(e))
