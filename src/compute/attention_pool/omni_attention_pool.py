"""
omni_attention_pool.py — Attention Pooling for Sequence Representations
Inspired by: FashionCLIP attention pooling + TVLT cross-modal pooling
Layer: Compute / AI

Learned attention pooling that adaptively weights sequence positions
for producing fixed-size representations from variable-length sequences.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict


class AttentionPool1D(nn.Module):
    """Learned attention pooling for 1D sequences.

    Uses a learnable query vector to attend over the sequence,
    producing a single pooled representation.
    """

    def __init__(self, dim: int, num_heads: int = 4):
        super().__init__()
        self.query = nn.Parameter(torch.randn(1, 1, dim) * 0.02)
        self.attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B = x.shape[0]
        query = self.query.expand(B, -1, -1)
        pooled, _ = self.attn(query, x, x, key_padding_mask=mask)
        return self.norm(pooled.squeeze(1))


class MultiQueryAttentionPool(nn.Module):
    """Multi-query attention pooling producing multiple summary vectors.

    Useful for extracting different aspects of the input sequence
    (e.g., content summary, style summary, semantic summary).
    """

    def __init__(self, dim: int, num_queries: int = 4, num_heads: int = 4):
        super().__init__()
        self.queries = nn.Parameter(torch.randn(1, num_queries, dim) * 0.02)
        self.attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.norm = nn.LayerNorm(dim)
        self.num_queries = num_queries

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B = x.shape[0]
        queries = self.queries.expand(B, -1, -1)
        pooled, _ = self.attn(queries, x, x, key_padding_mask=mask)
        return self.norm(pooled)


class GatedPool(nn.Module):
    """Gated pooling with learned importance weighting."""

    def __init__(self, dim: int):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Linear(dim, dim),
            nn.Sigmoid(),
        )
        self.proj = nn.Linear(dim, dim)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        gates = self.gate(x)
        gated = x * gates

        if mask is not None:
            gated = gated.masked_fill(mask.unsqueeze(-1), 0.0)
            lengths = (~mask).sum(dim=1, keepdim=True).clamp(min=1)
            pooled = gated.sum(dim=1) / lengths.float()
        else:
            pooled = gated.mean(dim=1)

        return self.norm(self.proj(pooled))


class HierarchicalPool(nn.Module):
    """Two-level hierarchical pooling for long sequences.

    First pools within local windows, then pools globally
    over the windowed representations.
    """

    def __init__(self, dim: int, window_size: int = 16, num_heads: int = 4):
        super().__init__()
        self.window_size = window_size
        self.local_pool = AttentionPool1D(dim, num_heads)
        self.global_pool = AttentionPool1D(dim, num_heads)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        # Pad to multiple of window_size
        pad_len = (self.window_size - T % self.window_size) % self.window_size
        if pad_len > 0:
            x = F.pad(x, (0, 0, 0, pad_len))

        num_windows = x.shape[1] // self.window_size
        # Reshape into windows
        windows = x.view(B * num_windows, self.window_size, D)

        # Local pooling within each window
        local_pooled = self.local_pool(windows)  # (B*W, D)
        local_pooled = local_pooled.view(B, num_windows, D)

        # Global pooling over windows
        global_pooled = self.global_pool(local_pooled)  # (B, D)
        return self.norm(global_pooled)


class OmniAttentionPool(nn.Module):
    """Unified attention pooling module with multiple strategies.

    Supports: attention, multi-query, gated, hierarchical, and mean pooling.
    """

    def __init__(self, dim: int, strategy: str = "attention",
                 num_heads: int = 4, num_queries: int = 4,
                 window_size: int = 16):
        super().__init__()
        self.strategy = strategy

        if strategy == "attention":
            self.pool = AttentionPool1D(dim, num_heads)
        elif strategy == "multi_query":
            self.pool = MultiQueryAttentionPool(dim, num_queries, num_heads)
        elif strategy == "gated":
            self.pool = GatedPool(dim)
        elif strategy == "hierarchical":
            self.pool = HierarchicalPool(dim, window_size, num_heads)
        elif strategy == "mean":
            self.pool = None
        else:
            raise ValueError(f"Unknown pooling strategy: {strategy}")

        self.output_proj = nn.Linear(dim, dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        if self.pool is None:
            # Mean pooling
            if mask is not None:
                x = x.masked_fill(mask.unsqueeze(-1), 0.0)
                lengths = (~mask).sum(dim=1, keepdim=True).clamp(min=1)
                pooled = x.sum(dim=1) / lengths.float()
            else:
                pooled = x.mean(dim=1)
        elif isinstance(self.pool, HierarchicalPool):
            pooled = self.pool(x)
        elif isinstance(self.pool, MultiQueryAttentionPool):
            pooled = self.pool(x, mask)
            pooled = pooled.mean(dim=1)  # Average across queries
        else:
            pooled = self.pool(x, mask)

        return self.output_proj(pooled)
