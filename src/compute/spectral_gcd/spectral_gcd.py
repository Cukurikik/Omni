import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class SpectralGCDComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[SpectralGCDComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class SpectralGCDEngine:
    """
    OMNI Engine: SpectralGCD
    Mathematical operations for Spectral Graph Convolutional Dynamics modeling generalized categories.
    """
    def __init__(self, epsilon: float = 1e-8):
        self.epsilon = epsilon

    def compute_graph_laplacian(self, adjacency_matrix: np.ndarray) -> Result:
        try:
            if not isinstance(adjacency_matrix, np.ndarray):
                return Result(None, SpectralGCDComputeError("Input must be np.ndarray"))
            if len(adjacency_matrix.shape) != 2 or adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
                return Result(None, SpectralGCDComputeError("Adjacency must be a square matrix"))
                
            # Symmetric normalized Laplacian D^{-1/2} (D - A) D^{-1/2}
            degree_vector = np.sum(adjacency_matrix, axis=1)
            
            if np.any(degree_vector == 0):
                return Result(None, SpectralGCDComputeError("Disconnected graph components detected, division by zero prevented"))
                
            d_inv_sqrt = np.power(degree_vector, -0.5)
            d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.0
            
            d_mat_inv_sqrt = np.diag(d_inv_sqrt)
            
            identity = np.eye(adjacency_matrix.shape[0])
            normalized_laplacian = identity - np.dot(d_mat_inv_sqrt, np.dot(adjacency_matrix, d_mat_inv_sqrt))
            
            return Result({'laplacian': normalized_laplacian, 'nodes': adjacency_matrix.shape[0]})
        except Exception as e:
            return Result(None, SpectralGCDComputeError(f"Laplacian computation failed: {str(e)}"))

    def compute_spectral_embeddings(self, normalized_laplacian: np.ndarray, k: int) -> Result:
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(normalized_laplacian)
            
            # Sort eigenvalues and eigenvectors
            idx = np.argsort(eigenvalues)
            sorted_evecs = eigenvectors[:, idx]
            
            if k > sorted_evecs.shape[1]:
                return Result(None, SpectralGCDComputeError(f"Requested k {k} exceeds dimensions {sorted_evecs.shape[1]}"))
                
            # Take first k non-trivial eigenvectors
            embeddings = sorted_evecs[:, 1:k+1]
            return Result({'spectral_embeddings': embeddings, 'top_eigenvalue': float(eigenvalues[idx[k]])})
        except Exception as e:
            return Result(None, SpectralGCDComputeError(f"Spectral embedding calc failed: {str(e)}"))
