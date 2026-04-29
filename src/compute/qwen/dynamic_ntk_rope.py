import math
import torch
from typing import Tuple, Optional

# OMNI QWEN: Dynamic NTK-aware RoPE
# Implements context length scaling dynamically based on sequence length, as used in Qwen models.
# Source: QwenLM/Qwen

class RoPEError(Exception):
    pass

def compute_dynamic_ntk_inv_freq(
    seq_len: int, 
    dim: int, 
    base: float = 10000.0, 
    max_position_embeddings: int = 2048
) -> Tuple[Optional[torch.Tensor], Optional[RoPEError]]:
    """
    Computes inverse frequencies for Rotary Position Embeddings using Dynamic NTK scaling.
    If the sequence length exceeds the model's trained max context, the base is scaled.
    """
    try:
        if dim <= 0 or dim % 2 != 0:
            return None, RoPEError("Dimension must be a positive even integer.")
            
        # Determine the scaling factor dynamically
        if seq_len > max_position_embeddings:
            # Dynamic NTK scaling formula
            # alpha = seq_len / max_position_embeddings
            # base' = base * alpha ^ (dim / (dim - 2))
            alpha = seq_len / max_position_embeddings
            base = base * (alpha ** (dim / (dim - 2)))
            
        # Generate the inverse frequencies
        # inv_freq = 1.0 / (base ^ (2i / dim)) for i in [0, dim/2)
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        
        return inv_freq, None

    except Exception as e:
        return None, RoPEError(f"Dynamic NTK RoPE calculation failed: {str(e)}")

def apply_rotary_pos_emb(
    q: torch.Tensor, 
    k: torch.Tensor, 
    cos: torch.Tensor, 
    sin: torch.Tensor, 
    position_ids: torch.Tensor
) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[RoPEError]]:
    """
    Applies the rotary position embeddings to queries and keys.
    """
    try:
        # q, k shapes: [batch, seq_len, num_heads, head_dim]
        # Gather cos/sin based on position_ids
        cos = cos.squeeze(1).squeeze(0)  # [seq_len, dim] -> shape matching depends on implementation
        sin = sin.squeeze(1).squeeze(0)
        
        # Simplified for structural representation
        # Real implementation rotates half the channels
        
        # We split the last dimension into two halves
        q1, q2 = q.chunk(2, dim=-1)
        k1, k2 = k.chunk(2, dim=-1)
        
        # Rotate half function: [-x2, x1]
        rotated_q = torch.cat((-q2, q1), dim=-1)
        rotated_k = torch.cat((-k2, k1), dim=-1)
        
        # Ensure cos/sin match broadcast shape
        cos = cos.unsqueeze(0).unsqueeze(2) # [1, seq_len, 1, head_dim]
        sin = sin.unsqueeze(0).unsqueeze(2)
        
        q_embed = (q * cos) + (rotated_q * sin)
        k_embed = (k * cos) + (rotated_k * sin)
        
        return q_embed, k_embed, None
        
    except Exception as e:
        return None, None, RoPEError(f"Rotary embedding application failed: {str(e)}")
