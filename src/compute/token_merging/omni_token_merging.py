"""
omni_token_merging.py — Token Merging for Efficient ViT Inference
Inspired by: ToMe + TVLT patch efficiency optimization
Layer: Compute / AI

Reduces token count in vision transformers by merging similar tokens
via bipartite soft matching, achieving 2x speedup with minimal quality loss.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


def bipartite_soft_matching(
    metric: torch.Tensor, r: int
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Match tokens in alternating sets using cosine similarity."""
    B, N, C = metric.shape
    with torch.no_grad():
        metric = F.normalize(metric, dim=-1)
        a_metric = metric[:, ::2]
        b_metric = metric[:, 1::2]
        scores = a_metric @ b_metric.transpose(-1, -2)
        node_max, node_idx = scores.max(dim=-1)
        edge_idx = node_max.argsort(dim=-1, descending=True)[..., None]
        src_idx = edge_idx[..., :r]
        dst_idx = node_idx[..., None].gather(dim=-2, index=src_idx)
    return src_idx, dst_idx


def merge_tokens(
    x: torch.Tensor, src_idx: torch.Tensor, dst_idx: torch.Tensor, r: int
) -> torch.Tensor:
    """Merge source tokens into destination tokens via averaging."""
    B, N, C = x.shape
    a, b = x[:, ::2], x[:, 1::2]

    src = a.gather(dim=-2, index=src_idx.expand(-1, -1, C))
    dst = b.scatter_reduce(-2, dst_idx.expand(-1, -1, C), src, reduce="mean")

    mask = torch.ones(B, a.shape[1], device=x.device, dtype=torch.bool)
    mask.scatter_(1, src_idx.squeeze(-1), False)
    unm = a[mask].reshape(B, -1, C)

    return torch.cat([unm, dst], dim=1)


def unmerge_tokens(
    merged: torch.Tensor, original_size: int,
    src_idx: torch.Tensor, dst_idx: torch.Tensor
) -> torch.Tensor:
    """Approximate inverse of token merging for reconstruction."""
    B, M, C = merged.shape
    output = torch.zeros(B, original_size, C, device=merged.device)
    half = original_size // 2
    unm_count = half - src_idx.shape[1]

    output[:, ::2, :][:, :unm_count] = merged[:, :unm_count]
    output[:, 1::2] = merged[:, unm_count:]

    dst_vals = merged[:, unm_count:].gather(
        dim=-2, index=dst_idx.expand(-1, -1, C)
    )
    output[:, ::2].scatter_(
        -2, src_idx.expand(-1, -1, C), dst_vals
    )

    return output


class OmniTokenMerging(nn.Module):
    """Drop-in module for token merging in ViT layers.

    Reduces sequence length by merge_ratio, then optionally
    unmerges for downstream tasks requiring full resolution.
    """

    def __init__(self, merge_ratio: float = 0.5):
        super().__init__()
        self.merge_ratio = merge_ratio
        self._src_idx = None
        self._dst_idx = None
        self._original_size = None

    def forward(self, x: torch.Tensor, metric: torch.Tensor = None) -> torch.Tensor:
        if metric is None:
            metric = x
        r = max(1, int(x.shape[1] * self.merge_ratio * 0.5))
        self._original_size = x.shape[1]
        self._src_idx, self._dst_idx = bipartite_soft_matching(metric, r)
        return merge_tokens(x, self._src_idx, self._dst_idx, r)

    def unmerge(self, x: torch.Tensor) -> torch.Tensor:
        if self._src_idx is None:
            return x
        return unmerge_tokens(x, self._original_size, self._src_idx, self._dst_idx)


class TokenMergingTransformerBlock(nn.Module):
    """Transformer block with integrated token merging."""

    def __init__(self, dim: int = 768, heads: int = 12, ff_mult: int = 4,
                 merge_ratio: float = 0.0, dropout: float = 0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, dim * ff_mult), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(dim * ff_mult, dim), nn.Dropout(dropout),
        )
        self.merger = OmniTokenMerging(merge_ratio) if merge_ratio > 0 else None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        normed = self.norm1(x)
        attn_out, _ = self.attn(normed, normed, normed)
        x = x + attn_out

        if self.merger is not None:
            x = self.merger(x)

        x = x + self.ff(self.norm2(x))
        return x
