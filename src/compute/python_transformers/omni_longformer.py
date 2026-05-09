"""OMNI Compute — Longformer (Dilated Sliding Window)"""
import logging
import math
from typing import List

logger = logging.getLogger("omni.longformer")

class LongformerAttention:
    """
    Longformer: The Long-Document Transformer.
    Uses local sliding window attention + global attention on selected tokens.
    """
    def __init__(self, window_size: int = 512, d_model: int = 768):
        self.window_size = window_size
        self.d_model = d_model
        logger.info(f"Initialized Longformer Attention (window={window_size})")

    def forward(self, hidden_states: List[List[float]], global_indices: List[int]) -> List[List[float]]:
        """
        Computes attention where each token attends to W local neighbors
        and specifically designated global tokens (e.g., [CLS]).
        """
        seq_len = len(hidden_states)
        output = [[0.0]*self.d_model for _ in range(seq_len)]
        
        half_w = self.window_size // 2
        
        for i in range(seq_len):
            context = [0.0]*self.d_model
            weight_sum = 0.0
            
            # Determine indices to attend to
            local_start = max(0, i - half_w)
            local_end = min(seq_len, i + half_w + 1)
            
            attend_indices = set(range(local_start, local_end))
            for g_idx in global_indices:
                if g_idx < seq_len:
                    attend_indices.add(g_idx)
                    
            # Compute attention over valid indices
            for j in attend_indices:
                # Dot product (Q_i * K_j)
                dot = sum(hidden_states[i][d] * hidden_states[j][d] for d in range(self.d_model))
                w = math.exp(dot / math.sqrt(self.d_model))
                weight_sum += w
                for d in range(self.d_model):
                    context[d] += w * hidden_states[j][d]
                    
            if weight_sum > 0:
                output[i] = [c / weight_sum for c in context]
                
        return output
