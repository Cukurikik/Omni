"""
OMNI Transformer — Sparse Attention Mechanisms
BigBird-style random+window+global sparse attention.
Learned from: thevasudevgupta/bigbird, Longformer patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
from dataclasses import dataclass
import random


@dataclass
class SparseAttentionConfig:
    embed_dim: int = 768
    num_heads: int = 12
    window_size: int = 128
    num_global_tokens: int = 2
    num_random_blocks: int = 3
    block_size: int = 64
    max_seq_len: int = 4096


class BigBirdAttention(nn.Module):
    """BigBird sparse attention: global + window + random."""
    def __init__(self, config: SparseAttentionConfig):
        super().__init__()
        self.config = config
        head_dim = config.embed_dim // config.num_heads
        self.scale = head_dim ** -0.5
        self.qkv = nn.Linear(config.embed_dim, config.embed_dim * 3)
        self.proj = nn.Linear(config.embed_dim, config.embed_dim)

    def _create_sparse_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create BigBird sparse attention mask."""
        mask = torch.zeros(seq_len, seq_len, device=device, dtype=torch.bool)
        # Global tokens (first N attend to all)
        g = self.config.num_global_tokens
        mask[:g, :] = True
        mask[:, :g] = True

        # Sliding window
        w = self.config.window_size // 2
        for i in range(seq_len):
            start = max(0, i - w)
            end = min(seq_len, i + w + 1)
            mask[i, start:end] = True

        # Random blocks
        bs = self.config.block_size
        num_blocks = seq_len // bs
        for i in range(num_blocks):
            for _ in range(self.config.num_random_blocks):
                j = random.randint(0, num_blocks - 1)
                mask[i*bs:(i+1)*bs, j*bs:(j+1)*bs] = True

        return mask

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, D = x.shape
        H = self.config.num_heads
        head_dim = D // H

        qkv = self.qkv(x).reshape(B, S, 3, H, head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        attn = (q @ k.transpose(-2, -1)) * self.scale

        # Apply sparse mask
        sparse_mask = self._create_sparse_mask(S, x.device)
        attn = attn.masked_fill(~sparse_mask.unsqueeze(0).unsqueeze(0), float("-inf"))

        attn = F.softmax(attn, dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, S, D)
        return self.proj(out)


class LinformerAttention(nn.Module):
    """Linformer linear attention with projected keys/values."""
    def __init__(self, embed_dim: int, num_heads: int, seq_len: int, k: int = 256):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(embed_dim, embed_dim * 3)
        self.E = nn.Linear(seq_len, k, bias=False)
        self.F_proj = nn.Linear(seq_len, k, bias=False)
        self.proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, D = x.shape
        H = self.num_heads

        qkv = self.qkv(x).reshape(B, S, 3, H, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv.unbind(0)

        # Project K, V to lower dimension
        k = self.E(k.transpose(-2, -1)).transpose(-2, -1)  # (B, H, k, head_dim)
        v = self.F_proj(v.transpose(-2, -1)).transpose(-2, -1)

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = F.softmax(attn, dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, S, D)
        return self.proj(out)
