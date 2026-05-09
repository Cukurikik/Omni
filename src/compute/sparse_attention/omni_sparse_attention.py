"""
omni_sparse_attention.py — Sparse Attention Mechanisms
Inspired by: BigBird/Longformer sparse patterns + Memformer
Layer: Compute / AI

Block-sparse attention patterns for efficient long-sequence
processing with O(n*sqrt(n)) complexity.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
import math


class SlidingWindowAttention(nn.Module):
    """Local sliding window attention with configurable window size."""

    def __init__(self, dim: int, heads: int = 8, window_size: int = 256,
                 dropout: float = 0.0):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.window_size = window_size
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def _sliding_window_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create sliding window attention mask."""
        mask = torch.ones(seq_len, seq_len, dtype=torch.bool, device=device)
        for i in range(seq_len):
            start = max(0, i - self.window_size // 2)
            end = min(seq_len, i + self.window_size // 2 + 1)
            mask[i, start:end] = False
        return mask  # True = masked out

    def forward(self, x: torch.Tensor,
                causal: bool = False) -> torch.Tensor:
        B, N, D = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        attn = (q @ k.transpose(-2, -1)) * self.scale

        # Apply window mask
        window_mask = self._sliding_window_mask(N, x.device)
        attn = attn.masked_fill(window_mask.unsqueeze(0).unsqueeze(0), float("-inf"))

        if causal:
            causal_mask = torch.triu(torch.ones(N, N, device=x.device, dtype=torch.bool), diagonal=1)
            attn = attn.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)

        out = (attn @ v).transpose(1, 2).reshape(B, N, D)
        return self.out_proj(out)


class GlobalTokenAttention(nn.Module):
    """Attention with designated global tokens that attend to all positions."""

    def __init__(self, dim: int, heads: int = 8, num_global_tokens: int = 4,
                 dropout: float = 0.0):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.num_global = num_global_tokens
        self.scale = self.head_dim ** -0.5

        self.global_tokens = nn.Parameter(torch.randn(1, num_global_tokens, dim) * 0.02)
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N, D = x.shape

        # Prepend global tokens
        global_tok = self.global_tokens.expand(B, -1, -1)
        x_with_global = torch.cat([global_tok, x], dim=1)
        total_len = x_with_global.shape[1]

        qkv = self.qkv(x_with_global).reshape(B, total_len, 3, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = F.softmax(attn, dim=-1)
        attn = self.dropout(attn)

        out = (attn @ v).transpose(1, 2).reshape(B, total_len, D)
        # Return only the non-global tokens
        return self.out_proj(out[:, self.num_global:])


class BlockSparseAttention(nn.Module):
    """Block-sparse attention splitting sequence into fixed-size blocks.

    Each block attends to itself and neighboring blocks,
    achieving O(n * block_size) complexity.
    """

    def __init__(self, dim: int, heads: int = 8, block_size: int = 64,
                 num_neighbor_blocks: int = 1, dropout: float = 0.0):
        super().__init__()
        self.heads = heads
        self.head_dim = dim // heads
        self.block_size = block_size
        self.num_neighbors = num_neighbor_blocks
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out_proj = nn.Linear(dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N, D = x.shape
        bs = self.block_size

        # Pad to multiple of block_size
        pad_len = (bs - N % bs) % bs
        if pad_len > 0:
            x = F.pad(x, (0, 0, 0, pad_len))

        padded_N = x.shape[1]
        num_blocks = padded_N // bs

        qkv = self.qkv(x).reshape(B, padded_N, 3, self.heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        # Reshape into blocks
        q = q.reshape(B, self.heads, num_blocks, bs, self.head_dim)
        k = k.reshape(B, self.heads, num_blocks, bs, self.head_dim)
        v = v.reshape(B, self.heads, num_blocks, bs, self.head_dim)

        output = torch.zeros_like(q)

        for block_idx in range(num_blocks):
            q_block = q[:, :, block_idx]  # (B, H, bs, hd)

            # Gather keys and values from neighboring blocks
            start = max(0, block_idx - self.num_neighbors)
            end = min(num_blocks, block_idx + self.num_neighbors + 1)

            k_neighbors = k[:, :, start:end].reshape(B, self.heads, -1, self.head_dim)
            v_neighbors = v[:, :, start:end].reshape(B, self.heads, -1, self.head_dim)

            attn = (q_block @ k_neighbors.transpose(-2, -1)) * self.scale
            attn = F.softmax(attn, dim=-1)
            attn = self.dropout(attn)

            output[:, :, block_idx] = attn @ v_neighbors

        output = output.reshape(B, self.heads, padded_N, self.head_dim)
        output = output.transpose(1, 2).reshape(B, padded_N, D)
        output = self.out_proj(output)

        return output[:, :N]


class OmniSparseAttention(nn.Module):
    """Combined sparse attention with local + global + random patterns."""

    def __init__(self, dim: int, heads: int = 8, window_size: int = 256,
                 num_global_tokens: int = 4, block_size: int = 64,
                 strategy: str = "sliding_window", dropout: float = 0.0):
        super().__init__()
        self.strategy = strategy

        if strategy == "sliding_window":
            self.attn = SlidingWindowAttention(dim, heads, window_size, dropout)
        elif strategy == "global_tokens":
            self.attn = GlobalTokenAttention(dim, heads, num_global_tokens, dropout)
        elif strategy == "block_sparse":
            self.attn = BlockSparseAttention(dim, heads, block_size, dropout=dropout)
        else:
            raise ValueError(f"Unknown sparse attention strategy: {strategy}")

        self.norm = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.norm(x))
        x = x + self.ff(x)
        return x
