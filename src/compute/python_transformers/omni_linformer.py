"""OMNI Compute — Linformer (Low-Rank Attention)"""
import logging
import math
from typing import List

logger = logging.getLogger("omni.linformer")

class LinformerAttention:
    """
    Linformer: Self-Attention with Linear Complexity.
    Projects the length dimension N to a lower dimensional space k.
    """
    def __init__(self, seq_len: int, proj_dim: int = 256, d_model: int = 512):
        self.seq_len = seq_len
        self.proj_dim = proj_dim
        self.d_model = d_model
        logger.info(f"Initialized Linformer Attention (seq_len={seq_len}, proj={proj_dim})")

    def _project_length(self, tensor: List[List[float]]) -> List[List[float]]:
        """Projects tensor of shape (N, d) to (k, d)."""
        projected = []
        n = len(tensor)
        # Simulate projection matrix E
        step = max(1, n // self.proj_dim)
        for i in range(0, n, step):
            if len(projected) >= self.proj_dim: break
            projected.append(tensor[i])
        
        # Pad if necessary
        while len(projected) < self.proj_dim:
            projected.append([0.0]*self.d_model)
            
        return projected

    def forward(self, queries: List[List[float]], keys: List[List[float]], values: List[List[float]]) -> List[List[float]]:
        """Linformer forward pass."""
        # 1. Project Keys and Values to low-rank k
        k_proj = self._project_length(keys)
        v_proj = self._project_length(values)
        
        output = []
        # 2. Standard attention with projected dimensions (N x k instead of N x N)
        for q in queries:
            context = [0.0]*self.d_model
            weight_sum = 0.0
            
            for j in range(len(k_proj)):
                dot = sum(q[d] * k_proj[j][d] for d in range(self.d_model))
                w = math.exp(dot / math.sqrt(self.d_model))
                weight_sum += w
                for d in range(self.d_model):
                    context[d] += w * v_proj[j][d]
            
            if weight_sum > 0:
                output.append([c / weight_sum for c in context])
            else:
                output.append([0.0]*self.d_model)
                
        return output
