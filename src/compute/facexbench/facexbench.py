import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class FacexBenchComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[FacexBenchComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class FacexBenchEngine:
    """
    OMNI Engine: facexbench
    Computes facial biometric similarity and cosine geometric clustering mathematically.
    """
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        num = np.dot(v1, v2)
        den = np.linalg.norm(v1) * np.linalg.norm(v2)
        if den == 0: return 0.0
        return float(num / den)

    def calculate_biometric_distance(self, emb1: np.ndarray, emb2: np.ndarray) -> Result:
        try:
            if not isinstance(emb1, np.ndarray) or not isinstance(emb2, np.ndarray):
                return Result(None, FacexBenchComputeError("Embeddings must be np.ndarray"))
                
            if emb1.shape[0] != 512 or emb2.shape[0] != 512:
                return Result(None, FacexBenchComputeError("Embeddings must be strictly 512-dimensional arrays"))
                
            sim = self._cosine_similarity(emb1, emb2)
            distance = 1.0 - sim
            
            is_match = bool(sim >= self.threshold)
            
            return Result({'similarity': sim, 'distance': distance, 'is_match': is_match})
        except Exception as e:
            return Result(None, FacexBenchComputeError(f"Distance calc failed: {str(e)}"))

    def compute_centroid_drift(self, batch_embeddings: np.ndarray, anchor: np.ndarray) -> Result:
        try:
            if batch_embeddings.shape[1] != 512 or anchor.shape[0] != 512:
                return Result(None, FacexBenchComputeError("Dimensional constraint violation (512 required)"))
                
            centroid = np.mean(batch_embeddings, axis=0)
            drift = self._cosine_similarity(centroid, anchor)
            
            return Result({'centroid_drift': drift, 'centroid_vector': centroid})
        except Exception as e:
            return Result(None, FacexBenchComputeError(f"Centroid computation error: {str(e)}"))
