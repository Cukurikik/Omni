import numpy as np

class OmniVectorIndex:
    def __init__(self, dim: int):
        self.dim = dim
        self.vectors = np.empty((0, dim))
        
    def add(self, vec: np.ndarray):
        if vec.shape[-1] != self.dim:
            raise ValueError("Dimension mismatch")
        self.vectors = np.vstack((self.vectors, vec))
        
    def search(self, query: np.ndarray, k: int) -> np.ndarray:
        if len(self.vectors) == 0:
            return np.array([])
        dists = np.linalg.norm(self.vectors - query, axis=1)
        return np.argsort(dists)[:k]
