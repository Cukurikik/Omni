"""
omni_rotary_embedding.py — Rotary Position Embedding (RoPE)
Layer: Compute / AI

Efficient, pure PyTorch implementation of Rotary Positional Embeddings
used in modern LLMs (Llama, Gemma). Fully unrolled mathematical logic,
zero mocks.
"""

import torch
import torch.nn as nn
from typing import Tuple

class OmniRotaryEmbedding(nn.Module):
    def __init__(self, dim: int, max_seq_len: int = 8192, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len
        self.base = base
        
        # Calculate theta frequencies
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)

        # Precompute cos and sin caches
        t = torch.arange(max_seq_len, dtype=torch.float32)
        freqs = torch.outer(t, self.inv_freq)
        
        # RoPE applies to pairs of dimensions, so we duplicate the freqs
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos()[None, None, :, :], persistent=False)
        self.register_buffer("sin_cached", emb.sin()[None, None, :, :], persistent=False)

    def forward(self, q: torch.Tensor, k: torch.Tensor, seq_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        q, k: (Batch, NumHeads, SeqLen, HeadDim)
        """
        cos = self.cos_cached[:, :, :seq_len, :]
        sin = self.sin_cached[:, :, :seq_len, :]
        
        q_out = (q * cos) + (self._rotate_half(q) * sin)
        k_out = (k * cos) + (self._rotate_half(k) * sin)
        
        return q_out, k_out

    def _rotate_half(self, x: torch.Tensor) -> torch.Tensor:
        """
        Rotates half the hidden dimensions of the input.
        """
        x1 = x[..., : x.shape[-1] // 2]
        x2 = x[..., x.shape[-1] // 2 :]
        return torch.cat((-x2, x1), dim=-1)
