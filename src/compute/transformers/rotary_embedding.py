import torch
import torch.nn as nn
from typing import Tuple, Optional

# OMNI TRANSFORMERS: Rotary Positional Embedding (RoPE)
# Python PyTorch logic for RoPE, essential for modern LLMs (Llama, Qwen, Mistral).
# Source: huggingface/transformers

class RoPEError(Exception):
    pass

class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, max_position_embeddings: int = 2048, base: float = 10000):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        
        # Calculate inverse frequencies
        # inv_freq = 1.0 / (base ^ (2i / dim))
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)

        # Build cache here to avoid recomputation
        self._set_cos_sin_cache(seq_len=max_position_embeddings)

    def _set_cos_sin_cache(self, seq_len: int):
        t = torch.arange(seq_len, device=self.inv_freq.device, dtype=self.inv_freq.dtype)
        # freqs = t \otimes inv_freq
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        
        # Concat to match full dimension: [seq_len, dim]
        emb = torch.cat((freqs, freqs), dim=-1)
        
        self.register_buffer("cos_cached", emb.cos()[None, None, :, :]) # [1, 1, seq_len, dim]
        self.register_buffer("sin_cached", emb.sin()[None, None, :, :])

    def forward(self, x: torch.Tensor, seq_len: int) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[RoPEError]]:
        try:
            if seq_len > self.max_position_embeddings:
                # Dynamic extension
                self._set_cos_sin_cache(seq_len=seq_len)

            # Slicing the cache for the current sequence length
            return (
                self.cos_cached[:, :, :seq_len, ...].to(x.dtype),
                self.sin_cached[:, :, :seq_len, ...].to(x.dtype),
                None
            )
        except Exception as e:
            return None, None, RoPEError(f"RoPE Forward Failed: {str(e)}")

def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Applies the cached cosine/sine embeddings to queries and keys."""
    # Rotate half tensor
    q1, q2 = q.chunk(2, dim=-1)
    k1, k2 = k.chunk(2, dim=-1)
    
    q_rot = torch.cat((-q2, q1), dim=-1)
    k_rot = torch.cat((-k2, k1), dim=-1)
    
    # Apply
    q_embed = (q * cos) + (q_rot * sin)
    k_embed = (k * cos) + (k_rot * sin)
    
    return q_embed, k_embed
