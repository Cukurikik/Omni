"""OMNI Compute — Rotary Position Embedding (RoPE)"""
import math
from typing import List, Tuple

def apply_rotary_pos_emb(q: List[List[float]], k: List[List[float]], seq_len: int, d_model: int) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Applies Rotary Position Embeddings (RoPE) to Queries and Keys.
    Simulated implementation for OMNI Transformer engines.
    """
    out_q = [[0.0]*d_model for _ in range(seq_len)]
    out_k = [[0.0]*d_model for _ in range(seq_len)]
    
    for pos in range(seq_len):
        for i in range(0, d_model, 2):
            # Calculate theta for this dimension pair
            theta = pos / (10000 ** (i / d_model))
            cos_val = math.cos(theta)
            sin_val = math.sin(theta)
            
            # Apply to query
            q0 = q[pos][i]
            q1 = q[pos][i+1]
            out_q[pos][i]   = q0 * cos_val - q1 * sin_val
            out_q[pos][i+1] = q1 * cos_val + q0 * sin_val
            
            # Apply to key
            k0 = k[pos][i]
            k1 = k[pos][i+1]
            out_k[pos][i]   = k0 * cos_val - k1 * sin_val
            out_k[pos][i+1] = k1 * cos_val + k0 * sin_val
            
    return out_q, out_k
