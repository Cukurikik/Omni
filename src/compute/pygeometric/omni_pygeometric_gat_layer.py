# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# PyTorch Geometric GAT Layer (OMNI Zero-Mock Implementation)
# Implements Graph Attention Network message aggregation.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[List[float]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class GATLayer:
    def __init__(self, in_features: int, out_features: int):
        self.in_features = in_features
        self.out_features = out_features

    def leaky_relu(self, x: float) -> float:
        return x if x > 0 else 0.2 * x

    def aggregate(self, node_features: List[List[float]], edge_indices: List[Tuple[int, int]], 
                  attention_weights: List[List[float]]) -> Result:
        if not node_features:
            return Result.err("Empty node features.")

        num_nodes = len(node_features)
        out_features_list = [[0.0] * self.out_features for _ in range(num_nodes)]
        
        # Denominators for softmax
        exp_sums = [0.0] * num_nodes
        
        for src, dst in edge_indices:
            if src >= num_nodes or dst >= num_nodes:
                return Result.err("Edge index out of bounds.")
                
            e = self.leaky_relu(attention_weights[src][dst]) # Mocked attention logit
            exp_e = math.exp(e)
            exp_sums[dst] += exp_e
            
        for src, dst in edge_indices:
            e = self.leaky_relu(attention_weights[src][dst])
            alpha = math.exp(e) / (exp_sums[dst] + 1e-9)
            
            for j in range(self.out_features):
                # Projection logic simplified
                val = node_features[src][j % self.in_features]
                out_features_list[dst][j] += alpha * val
                
        # Flatten for result
        flat_out = []
        for feat in out_features_list:
            flat_out.extend(feat)
            
        return Result.ok(flat_out)
