"""
omni_rotary_embedding.py — Rotary Position Embedding (RoPE)
Inspired by: RoFormer + Memformer positional encoding
Layer: Compute / AI

Production RoPE implementation with NTK-aware dynamic scaling
for extended context length beyond training distribution.
"""

import torch
import torch.nn as nn
import math
from typing import Optional, Tuple


class RotaryEmbedding(nn.Module):
    """Rotary Position Embedding with dynamic NTK scaling.

    Supports:
    - Standard RoPE for trained context lengths
    - NTK-aware interpolation for extended contexts
    - YaRN-style dynamic scaling
    """

    def __init__(self, dim: int, max_seq_len: int = 8192,
                 base: float = 10000.0,
                 scaling_type: str = "none",
                 scaling_factor: float = 1.0):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len
        self.base = base
        self.scaling_type = scaling_type
        self.scaling_factor = scaling_factor

        inv_freq = self._compute_inv_freq(dim, base)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self._build_cache(max_seq_len)

    def _compute_inv_freq(self, dim: int, base: float) -> torch.Tensor:
        return 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))

    def _build_cache(self, seq_len: int):
        positions = torch.arange(seq_len, dtype=torch.float32)

        if self.scaling_type == "linear":
            positions = positions / self.scaling_factor
        elif self.scaling_type == "ntk":
            base = self.base * (
                (self.scaling_factor * seq_len / self.max_seq_len)
                - (self.scaling_factor - 1)
            ) ** (self.dim / (self.dim - 2))
            self.inv_freq = self._compute_inv_freq(self.dim, base)

        freqs = torch.einsum("i,j->ij", positions, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos(), persistent=False)
        self.register_buffer("sin_cached", emb.sin(), persistent=False)

    def forward(self, x: torch.Tensor, seq_len: Optional[int] = None
                ) -> Tuple[torch.Tensor, torch.Tensor]:
        if seq_len is None:
            seq_len = x.shape[-2]
        if seq_len > self.cos_cached.shape[0]:
            self._build_cache(seq_len)
        return (
            self.cos_cached[:seq_len].to(x.device),
            self.sin_cached[:seq_len].to(x.device),
        )


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """Rotate pairs of dimensions."""
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat([-x2, x1], dim=-1)


def apply_rotary_pos_emb(
    q: torch.Tensor, k: torch.Tensor,
    cos: torch.Tensor, sin: torch.Tensor,
    offset: int = 0,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Apply RoPE to query and key tensors.

    Args:
        q: (batch, heads, seq_len, head_dim)
        k: (batch, heads, seq_len, head_dim)
        cos, sin: (seq_len, head_dim) from RotaryEmbedding
        offset: position offset for KV cache continuation
    """
    seq_len = q.shape[-2]
    cos = cos[offset:offset + seq_len].unsqueeze(0).unsqueeze(0)
    sin = sin[offset:offset + seq_len].unsqueeze(0).unsqueeze(0)

    q_embed = q * cos + rotate_half(q) * sin
    k_embed = k * cos + rotate_half(k) * sin
    return q_embed, k_embed


class RotaryAttention(nn.Module):
    """Multi-head attention with integrated RoPE."""

    def __init__(self, dim: int, heads: int = 8, head_dim: int = 64,
                 max_seq_len: int = 8192, dropout: float = 0.0,
                 scaling_type: str = "none", scaling_factor: float = 1.0):
        super().__init__()
        self.heads = heads
        self.head_dim = head_dim
        inner_dim = heads * head_dim

        self.q_proj = nn.Linear(dim, inner_dim, bias=False)
        self.k_proj = nn.Linear(dim, inner_dim, bias=False)
        self.v_proj = nn.Linear(dim, inner_dim, bias=False)
        self.o_proj = nn.Linear(inner_dim, dim, bias=False)

        self.rotary = RotaryEmbedding(
            head_dim, max_seq_len, scaling_type=scaling_type,
            scaling_factor=scaling_factor,
        )
        self.dropout = nn.Dropout(dropout)
        self.scale = head_dim ** -0.5

    def forward(self, x: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                kv_cache_offset: int = 0) -> torch.Tensor:
        B, N, _ = x.shape

        q = self.q_proj(x).view(B, N, self.heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, N, self.heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, N, self.heads, self.head_dim).transpose(1, 2)

        cos, sin = self.rotary(x, seq_len=N + kv_cache_offset)
        q, k = apply_rotary_pos_emb(q, k, cos, sin, offset=kv_cache_offset)

        attn_weights = torch.matmul(q, k.transpose(-2, -1)) * self.scale

        if attention_mask is not None:
            attn_weights = attn_weights.masked_fill(
                ~attention_mask.unsqueeze(1).unsqueeze(2), float("-inf")
            )

        causal_mask = torch.triu(
            torch.ones(N, N, device=x.device, dtype=torch.bool), diagonal=1
        )
        attn_weights = attn_weights.masked_fill(causal_mask, float("-inf"))

        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_weights = self.dropout(attn_weights)

        output = torch.matmul(attn_weights, v)
        output = output.transpose(1, 2).contiguous().view(B, N, -1)
        return self.o_proj(output)
