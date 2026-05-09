"""
OMNI Transformer Engine — Scaled Dot-Product Attention
Production-grade implementation with FlashAttention fallback.
Learned from: Dao-AILab/flash-attention, IDSIA/recurrent-fwp (NeurIPS 2021)

This module provides:
  - Standard scaled dot-product attention
  - Memory-efficient chunked attention for long sequences
  - Causal masking support
  - Multi-query and grouped-query attention variants
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class AttentionType(Enum):
    STANDARD = auto()
    FLASH = auto()
    CHUNKED = auto()
    LINEAR = auto()


@dataclass(frozen=True)
class AttentionConfig:
    """Immutable configuration for attention computation."""
    embed_dim: int
    num_heads: int
    num_kv_heads: Optional[int] = None  # For GQA/MQA
    head_dim: Optional[int] = None
    dropout: float = 0.0
    causal: bool = False
    attention_type: AttentionType = AttentionType.STANDARD
    chunk_size: int = 512
    scale: Optional[float] = None
    max_seq_len: int = 8192

    def __post_init__(self):
        if self.head_dim is None:
            object.__setattr__(self, 'head_dim', self.embed_dim // self.num_heads)
        if self.num_kv_heads is None:
            object.__setattr__(self, 'num_kv_heads', self.num_heads)
        if self.scale is None:
            object.__setattr__(self, 'scale', 1.0 / math.sqrt(self.head_dim))

    @property
    def kv_groups(self) -> int:
        return self.num_heads // self.num_kv_heads


def _compute_causal_mask(
    seq_len_q: int,
    seq_len_k: int,
    device: torch.device,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Generate lower-triangular causal mask."""
    mask = torch.triu(
        torch.ones(seq_len_q, seq_len_k, device=device, dtype=dtype),
        diagonal=seq_len_k - seq_len_q + 1,
    )
    return mask.masked_fill(mask.bool(), float("-inf"))


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    config: AttentionConfig,
    attn_mask: Optional[torch.Tensor] = None,
    is_training: bool = False,
) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
    """
    Compute scaled dot-product attention.

    Args:
        query:  (B, H, S_q, D)
        key:    (B, H_kv, S_k, D)
        value:  (B, H_kv, S_k, D)
        config: AttentionConfig
        attn_mask: Optional additive mask (B, H, S_q, S_k) or (S_q, S_k)
        is_training: Whether in training mode (affects dropout)

    Returns:
        Tuple of (output, attention_weights)
        output: (B, H, S_q, D)
        attention_weights: (B, H, S_q, S_k) or None
    """
    B, H_q, S_q, D = query.shape
    _, H_kv, S_k, _ = key.shape

    # Handle Grouped-Query Attention (GQA) by repeating KV heads
    if H_kv < H_q:
        repeat_factor = H_q // H_kv
        key = key.repeat_interleave(repeat_factor, dim=1)
        value = value.repeat_interleave(repeat_factor, dim=1)

    if config.attention_type == AttentionType.FLASH and hasattr(F, 'scaled_dot_product_attention'):
        return _flash_attention(query, key, value, config, attn_mask, is_training)
    elif config.attention_type == AttentionType.CHUNKED:
        return _chunked_attention(query, key, value, config, attn_mask, is_training)
    elif config.attention_type == AttentionType.LINEAR:
        return _linear_attention(query, key, value, config, is_training)

    return _standard_attention(query, key, value, config, attn_mask, is_training)


def _standard_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    config: AttentionConfig,
    attn_mask: Optional[torch.Tensor],
    is_training: bool,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Standard O(n^2) attention with full materialization."""
    attn_weights = torch.matmul(query, key.transpose(-2, -1)) * config.scale

    if config.causal:
        causal_mask = _compute_causal_mask(
            query.size(-2), key.size(-2), query.device, query.dtype
        )
        attn_weights = attn_weights + causal_mask

    if attn_mask is not None:
        attn_weights = attn_weights + attn_mask

    attn_weights = F.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)

    if is_training and config.dropout > 0.0:
        attn_weights = F.dropout(attn_weights, p=config.dropout, training=True)

    output = torch.matmul(attn_weights, value)
    return output, attn_weights


def _flash_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    config: AttentionConfig,
    attn_mask: Optional[torch.Tensor],
    is_training: bool,
) -> Tuple[torch.Tensor, None]:
    """PyTorch 2.0+ FlashAttention via F.scaled_dot_product_attention."""
    dropout_p = config.dropout if is_training else 0.0
    output = F.scaled_dot_product_attention(
        query, key, value,
        attn_mask=attn_mask,
        dropout_p=dropout_p,
        is_causal=config.causal and attn_mask is None,
        scale=config.scale,
    )
    return output, None


def _chunked_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    config: AttentionConfig,
    attn_mask: Optional[torch.Tensor],
    is_training: bool,
) -> Tuple[torch.Tensor, None]:
    """Memory-efficient chunked attention for very long sequences."""
    B, H, S_q, D = query.shape
    chunk_size = config.chunk_size
    outputs = []

    for start in range(0, S_q, chunk_size):
        end = min(start + chunk_size, S_q)
        q_chunk = query[:, :, start:end, :]

        chunk_mask = None
        if config.causal:
            chunk_mask = _compute_causal_mask(
                end - start, key.size(-2), query.device, query.dtype
            )
            # Shift for chunk position
            if start > 0:
                prefix_mask = torch.zeros(
                    end - start, start, device=query.device, dtype=query.dtype
                )
                chunk_mask = torch.cat([prefix_mask, chunk_mask[:, start:]], dim=-1)

        attn_w = torch.matmul(q_chunk, key.transpose(-2, -1)) * config.scale

        if chunk_mask is not None:
            attn_w = attn_w + chunk_mask.unsqueeze(0).unsqueeze(0)

        if attn_mask is not None:
            attn_w = attn_w + attn_mask[:, :, start:end, :]

        attn_w = F.softmax(attn_w, dim=-1, dtype=torch.float32).to(query.dtype)
        if is_training and config.dropout > 0.0:
            attn_w = F.dropout(attn_w, p=config.dropout, training=True)

        outputs.append(torch.matmul(attn_w, value))

    return torch.cat(outputs, dim=2), None


def _linear_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    config: AttentionConfig,
    is_training: bool,
) -> Tuple[torch.Tensor, None]:
    """
    Linear attention O(n) approximation using kernel feature maps.
    Inspired by IDSIA/recurrent-fwp fast weight programmers.
    """
    # Apply ELU + 1 feature map (ensures non-negative)
    q_prime = F.elu(query) + 1.0
    k_prime = F.elu(key) + 1.0

    # Linear attention: (Q' @ (K'^T @ V)) / (Q' @ K'^T @ 1)
    kv = torch.matmul(k_prime.transpose(-2, -1), value)  # (B, H, D, D)
    numerator = torch.matmul(q_prime, kv)  # (B, H, S_q, D)

    k_sum = k_prime.sum(dim=-2, keepdim=True)  # (B, H, 1, D)
    denominator = torch.matmul(q_prime, k_sum.transpose(-2, -1))  # (B, H, S_q, 1)
    denominator = denominator.clamp(min=1e-6)

    output = numerator / denominator

    if is_training and config.dropout > 0.0:
        output = F.dropout(output, p=config.dropout, training=True)

    return output, None


class ScaledDotProductAttention(nn.Module):
    """
    PyTorch module wrapper for scaled dot-product attention.
    Supports standard, flash, chunked, and linear attention.
    """

    def __init__(self, config: AttentionConfig):
        super().__init__()
        self.config = config

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attn_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        return scaled_dot_product_attention(
            query, key, value, self.config, attn_mask, self.training
        )

    def extra_repr(self) -> str:
        return (
            f"type={self.config.attention_type.name}, "
            f"heads={self.config.num_heads}, "
            f"head_dim={self.config.head_dim}, "
            f"causal={self.config.causal}"
        )
