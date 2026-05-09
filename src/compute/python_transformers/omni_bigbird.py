"""OMNI Compute — BigBird Sparse Attention"""
import logging
import math
from typing import List

logger = logging.getLogger("omni.bigbird")

class BigBirdAttention:
    """
    BigBird: Transformers for Longer Sequences.
    Combines Random attention, Window attention, and Global attention.
    """
    def __init__(self, window_size: int = 3, num_random_blocks: int = 2, d_model: int = 256):
        self.window_size = window_size
        self.num_random_blocks = num_random_blocks
        self.d_model = d_model
        logger.info(f"Initialized BigBird Sparse Attention")

    def forward(self, hidden_states: List[List[float]], global_indices: List[int]) -> List[List[float]]:
        """Simulates BigBird sparse attention mechanism."""
        seq_len = len(hidden_states)
        output = [[0.0]*self.d_model for _ in range(seq_len)]
        
        import random
        
        for i in range(seq_len):
            context = [0.0]*self.d_model
            weight_sum = 0.0
            
            attend_indices = set()
            
            # 1. Global Attention
            for g in global_indices:
                if g < seq_len: attend_indices.add(g)
            
            # 2. Window Attention
            for w in range(max(0, i - self.window_size), min(seq_len, i + self.window_size + 1)):
                attend_indices.add(w)
                
            # 3. Random Attention
            for _ in range(self.num_random_blocks):
                attend_indices.add(random.randint(0, seq_len - 1))
                
            for j in attend_indices:
                dot = sum(hidden_states[i][d] * hidden_states[j][d] for d in range(self.d_model))
                w_val = math.exp(min(dot / math.sqrt(self.d_model), 20.0))
                weight_sum += w_val
                for d in range(self.d_model):
                    context[d] += w_val * hidden_states[j][d]
                    
            if weight_sum > 0:
                output[i] = [c / weight_sum for c in context]
                
        return output
