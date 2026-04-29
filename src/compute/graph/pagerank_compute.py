import numpy as np
from typing import Any

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class PageRankEngine:
    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6):
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def compute(self, adjacency_matrix: np.ndarray) -> OmniResult:
        """
        Computes PageRank for a given square adjacency matrix.
        """
        if adjacency_matrix is None or len(adjacency_matrix.shape) != 2 or adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
            return OmniResult.err("Invalid input: adjacency_matrix must be a square 2D numpy array")
            
        try:
            n_nodes = adjacency_matrix.shape[0]
            if n_nodes == 0:
                return OmniResult.ok(np.array([]))

            # Normalize adjacency matrix (out-degree)
            out_degree = np.sum(adjacency_matrix, axis=1)
            # Handle sinks (nodes with no outgoing edges)
            out_degree[out_degree == 0] = 1 
            
            transition_matrix = adjacency_matrix / out_degree[:, np.newaxis]
            
            # Initialize ranks
            ranks = np.ones(n_nodes) / n_nodes
            
            for _ in range(self.max_iterations):
                prev_ranks = np.copy(ranks)
                
                # PR(A) = (1-d)/N + d * sum(PR(Ti)/C(Ti))
                ranks = (1 - self.damping_factor) / n_nodes + self.damping_factor * np.dot(transition_matrix.T, ranks)
                
                # Check convergence
                if np.sum(np.abs(ranks - prev_ranks)) < self.tolerance:
                    break
                    
            return OmniResult.ok(ranks)
        except Exception as e:
            return OmniResult.err(f"PageRank computation failed: {str(e)}")
