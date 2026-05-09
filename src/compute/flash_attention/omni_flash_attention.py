"""
omni_flash_attention.py — Flash Attention Implementation
Inspired by: FlashAttention-2 + Memformer memory efficiency
Layer: Compute / AI

Memory-efficient attention with tiled computation, online softmax,
and fused operations for O(N) memory complexity.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
import math


class TiledAttention(nn.Module):
    """Tiled attention that processes queries/keys in blocks.

    Reduces peak memory from O(N^2) to O(N * block_size) by
    computing attention in tiles with online softmax accumulation.
    """

    def __init__(self, dim: int, heads: int = 8, block_size: int = 256,
                 dropout: float = 0.0, causal: bool = False):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.block_size = block_size
        self.scale = self.head_dim ** -0.5
        self.causal = causal

        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def _tiled_attention(self, q: torch.Tensor, k: torch.Tensor,
                         v: torch.Tensor) -> torch.Tensor:
        """Compute attention using tiled blocks with online softmax."""
        B, H, N, D = q.shape
        bs = self.block_size

        output = torch.zeros_like(q)
        row_max = torch.full((B, H, N, 1), float("-inf"), device=q.device, dtype=q.dtype)
        row_sum = torch.zeros(B, H, N, 1, device=q.device, dtype=q.dtype)

        num_blocks = (N + bs - 1) // bs

        for j in range(num_blocks):
            j_start = j * bs
            j_end = min(j_start + bs, N)

            k_block = k[:, :, j_start:j_end]  # (B, H, bs_j, D)
            v_block = v[:, :, j_start:j_end]  # (B, H, bs_j, D)

            # Compute attention scores for this block
            scores = torch.matmul(q, k_block.transpose(-2, -1)) * self.scale  # (B, H, N, bs_j)

            # Apply causal mask if needed
            if self.causal:
                query_positions = torch.arange(N, device=q.device).unsqueeze(1)
                key_positions = torch.arange(j_start, j_end, device=q.device).unsqueeze(0)
                causal_mask = query_positions < key_positions
                scores = scores.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float("-inf"))

            # Online softmax update
            block_max = scores.amax(dim=-1, keepdim=True)
            new_max = torch.maximum(row_max, block_max)

            # Rescale previous accumulations
            exp_old = torch.exp(row_max - new_max)
            exp_new = torch.exp(scores - new_max)

            # Update running sum
            new_sum = row_sum * exp_old + exp_new.sum(dim=-1, keepdim=True)

            # Update output: rescale old output and add new contribution
            output = output * (row_sum * exp_old / new_sum.clamp(min=1e-10))
            output = output + torch.matmul(exp_new, v_block) / new_sum.clamp(min=1e-10)

            row_max = new_max
            row_sum = new_sum

        return output

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, N, D = x.shape

        qkv = self.qkv(x).reshape(B, N, 3, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        # Use native scaled_dot_product_attention if available (PyTorch 2.0+)
        if hasattr(F, "scaled_dot_product_attention") and not self.training:
            out = F.scaled_dot_product_attention(
                q, k, v, is_causal=self.causal,
                dropout_p=self.dropout.p if self.training else 0.0,
            )
        else:
            out = self._tiled_attention(q, k, v)
            if self.training:
                out = self.dropout(out)

        out = out.transpose(1, 2).reshape(B, N, D)
        return self.out_proj(out)


class FlashCrossAttention(nn.Module):
    """Memory-efficient cross-attention for encoder-decoder models."""

    def __init__(self, dim: int, heads: int = 8, block_size: int = 256,
                 dropout: float = 0.0):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.block_size = block_size
        self.scale = self.head_dim ** -0.5

        self.q_proj = nn.Linear(dim, dim, bias=False)
        self.kv_proj = nn.Linear(dim, dim * 2, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, query: torch.Tensor, context: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, N_q, D = query.shape
        N_kv = context.shape[1]

        q = self.q_proj(query).reshape(B, N_q, self.heads, self.head_dim).transpose(1, 2)
        kv = self.kv_proj(context).reshape(B, N_kv, 2, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        k, v = kv.unbind(0)

        if hasattr(F, "scaled_dot_product_attention"):
            attn_mask = None
            if mask is not None:
                attn_mask = mask.unsqueeze(1).unsqueeze(2)
            out = F.scaled_dot_product_attention(
                q, k, v, attn_mask=attn_mask,
                dropout_p=self.dropout.p if self.training else 0.0,
            )
        else:
            attn = (q @ k.transpose(-2, -1)) * self.scale
            if mask is not None:
                attn = attn.masked_fill(mask.unsqueeze(1).unsqueeze(2), float("-inf"))
            attn = F.softmax(attn, dim=-1)
            attn = self.dropout(attn)
            out = attn @ v

        out = out.transpose(1, 2).reshape(B, N_q, D)
        return self.out_proj(out)


class OmniFlashAttentionBlock(nn.Module):
    """Pre-norm transformer block with flash attention."""

    def __init__(self, dim: int, heads: int = 8, ff_mult: int = 4,
                 block_size: int = 256, dropout: float = 0.0,
                 causal: bool = False):
        super().__init__()
        self.attn_norm = nn.LayerNorm(dim)
        self.attn = TiledAttention(dim, heads, block_size, dropout, causal)

        self.ff_norm = nn.LayerNorm(dim)
        ff_dim = dim * ff_mult
        self.ff = nn.Sequential(
            nn.Linear(dim, ff_dim, bias=False),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, dim, bias=False),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = x + self.attn(self.attn_norm(x), mask)
        x = x + self.ff(self.ff_norm(x))
        return x


class OmniFlashTransformer(nn.Module):
    """Stack of flash attention blocks."""

    def __init__(self, dim: int = 768, depth: int = 12, heads: int = 12,
                 ff_mult: int = 4, block_size: int = 256,
                 dropout: float = 0.0, causal: bool = False):
        super().__init__()
        self.layers = nn.ModuleList([
            OmniFlashAttentionBlock(dim, heads, ff_mult, block_size, dropout, causal)
            for _ in range(depth)
        ])
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x, mask)
        return self.norm(x)
