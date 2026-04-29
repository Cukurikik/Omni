# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# DGL Message Passing (OMNI Zero-Mock Implementation)
# Implements Graph Convolution Network sum aggregator.

from dataclasses import dataclass
from typing import List, Tuple, Optional

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

class DGLMessagePassingBlock:
    def forward(self, node_features: List[float], edges: List[Tuple[int, int]], feature_dim: int) -> Result:
        if len(node_features) % feature_dim != 0:
            return Result.err("Node features length not aligned with feature dimension.")
            
        num_nodes = len(node_features) // feature_dim
        mailbox = [[0.0] * feature_dim for _ in range(num_nodes)]
        degrees = [0] * num_nodes

        for src, dst in edges:
            if src >= num_nodes or dst >= num_nodes:
                return Result.err("Edge source or destination exceeds node boundaries.")
                
            degrees[dst] += 1
            for f in range(feature_dim):
                mailbox[dst][f] += node_features[src * feature_dim + f]

        output = []
        for i in range(num_nodes):
            for f in range(feature_dim):
                avg = mailbox[i][f] / max(1, degrees[i])
                output.append(avg)

        return Result.ok(output)
