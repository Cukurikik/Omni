import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class HypergraphComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[HypergraphComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class HypergraphRouterEngine:
    """
    OMNI Engine: hypergraph-attention
    Mathematical modeling of multi-node incidence matrices for n-ary relationships.
    """
    def __init__(self, attention_spill_factor: float = 0.1):
        self.spill_factor = attention_spill_factor

    def compute_incidence_degree(self, incidence_matrix: np.ndarray) -> Result:
        # Incidence matrix [Nodes x Hyperedges]
        try:
            if len(incidence_matrix.shape) != 2:
                return Result(None, HypergraphComputeError("Geometry structurally invalid: Requires 2D Node x Edge array"))
                
            node_degrees = np.sum(incidence_matrix, axis=1)
            hyperedge_degrees = np.sum(incidence_matrix, axis=0)
            
            if np.any(hyperedge_degrees == 0):
                  return Result(None, HypergraphComputeError("Hypergraph contains ghost edges (Zero nodes connected)"))
                  
            return Result({'avg_node_degree': float(np.mean(node_degrees)), 'avg_edge_degree': float(np.mean(hyperedge_degrees))})
        except Exception as e:
            return Result(None, HypergraphComputeError(f"Incidence map destroyed: {str(e)}"))

    def calculate_hypergraph_attention_spill(self, node_activations: np.ndarray, incidence_matrix: np.ndarray) -> Result:
         try:
              if node_activations.shape[0] != incidence_matrix.shape[0]:
                   return Result(None, HypergraphComputeError("Nodes and activations dimensions are misaligned"))
                   
              # Spill across hyperedges: (H^T * W_e * H * Activations)
              # Simple form: 
              edge_activations = np.dot(incidence_matrix.T, node_activations)
              spillback_activations = np.dot(incidence_matrix, edge_activations) * self.spill_factor
              
              max_spill = float(np.max(spillback_activations))
              
              return Result({'spill_activations': spillback_activations, 'is_overflowing': max_spill > 5.0})
         except Exception as e:
              return Result(None, HypergraphComputeError(f"Spill calculus broken: {str(e)}"))
