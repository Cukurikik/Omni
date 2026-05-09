"""OMNI Compute — Set Transformer"""
import logging
import math
from typing import List

logger = logging.getLogger("omni.set_transformer")

class SetTransformer:
    """
    Set Transformer: A Framework for Attention-based Permutation-Invariant Neural Networks.
    Uses Multihead Attention Blocks (MAB) and Pooling by Multihead Attention (PMA).
    """
    def __init__(self, d_model: int = 128, num_inducing_points: int = 32):
        self.d_model = d_model
        self.k = num_inducing_points
        # Inducing points for PMA (learnable parameters)
        self.inducing_points = [[0.01 * i for i in range(d_model)] for _ in range(self.k)]
        logger.info(f"Initialized Set Transformer (inducing_points={self.k})")

    def _mab(self, x: List[List[float]], y: List[List[float]]) -> List[List[float]]:
        """Multihead Attention Block. Q=x, K=y, V=y."""
        output = []
        for q in x:
            context = [0.0]*self.d_model
            weight_sum = 0.0
            for k_v in y:
                dot = sum(q[d] * k_v[d] for d in range(self.d_model))
                w = math.exp(min(dot / math.sqrt(self.d_model), 20.0))
                weight_sum += w
                for d in range(self.d_model):
                    context[d] += w * k_v[d]
            output.append([c / max(weight_sum, 1e-9) for c in context])
        return output

    def forward(self, input_set: List[List[float]]) -> List[float]:
        """
        Permutation invariant forward pass.
        1. Self-attention on set elements
        2. Pooling via inducing points
        """
        if not input_set: return [0.0] * self.d_model
        
        # SAB: Self-Attention Block (MAB with X, X)
        h = self._mab(input_set, input_set)
        
        # PMA: Pooling by Multihead Attention (MAB with Inducing Points, H)
        pooled = self._mab(self.inducing_points, h)
        
        # Aggregate pooled features (e.g. mean)
        final_out = [0.0]*self.d_model
        for p in pooled:
            for d in range(self.d_model):
                final_out[d] += p[d]
        return [f / self.k for f in final_out]
