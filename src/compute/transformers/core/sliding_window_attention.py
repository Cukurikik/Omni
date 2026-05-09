"""
OMNI Transformer — Sliding Window Attention for Long Context
Efficient attention for extremely long sequences.
Learned from: Mistral, Longformer patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class SlidingWindowConfig:
    embed_dim: int = 4096
    num_heads: int = 32
    num_kv_heads: int = 8
    head_dim: int = 128
    window_size: int = 4096
    max_seq_len: int = 32768


class SlidingWindowAttention(nn.Module):
    """Sliding window attention for very long context (Mistral-style)."""
    def __init__(self, config: SlidingWindowConfig):
        super().__init__()
        self.config = config
        self.q_proj = nn.Linear(config.embed_dim, config.num_heads * config.head_dim, bias=False)
        self.k_proj = nn.Linear(config.embed_dim, config.num_kv_heads * config.head_dim, bias=False)
        self.v_proj = nn.Linear(config.embed_dim, config.num_kv_heads * config.head_dim, bias=False)
        self.o_proj = nn.Linear(config.num_heads * config.head_dim, config.embed_dim, bias=False)
        self.scale = config.head_dim ** -0.5

    def forward(self, x: torch.Tensor, kv_cache: Optional[Tuple] = None,
                use_cache: bool = False) -> Tuple[torch.Tensor, Optional[Tuple]]:
        B, S, _ = x.shape

        q = self.q_proj(x).view(B, S, self.config.num_heads, self.config.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, S, self.config.num_kv_heads, self.config.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, S, self.config.num_kv_heads, self.config.head_dim).transpose(1, 2)

        # Handle KV cache
        if kv_cache is not None:
            cached_k, cached_v = kv_cache
            k = torch.cat([cached_k, k], dim=2)
            v = torch.cat([cached_v, v], dim=2)
            # Trim to window size
            if k.size(2) > self.config.window_size:
                k = k[:, :, -self.config.window_size:]
                v = v[:, :, -self.config.window_size:]

        new_cache = (k, v) if use_cache else None

        # GQA expansion
        if self.config.num_kv_heads < self.config.num_heads:
            repeat = self.config.num_heads // self.config.num_kv_heads
            k = k.repeat_interleave(repeat, dim=1)
            v = v.repeat_interleave(repeat, dim=1)

        # Standard attention within window
        attn = (q @ k.transpose(-2, -1)) * self.scale

        # Causal + sliding window mask
        S_k = k.size(2)
        causal_mask = torch.triu(torch.ones(S, S_k, device=x.device, dtype=torch.bool), diagonal=S_k - S + 1)
        window_mask = torch.ones(S, S_k, device=x.device, dtype=torch.bool)
        for i in range(S):
            start = max(0, S_k - S + i - self.config.window_size + 1)
            end = S_k - S + i + 1
            window_mask[i, start:end] = False
        combined_mask = causal_mask | window_mask
        attn = attn.masked_fill(combined_mask.unsqueeze(0).unsqueeze(0), float("-inf"))

        attn = F.softmax(attn, dim=-1)
        out = (attn @ v).transpose(1, 2).contiguous().view(B, S, -1)
        return self.o_proj(out), new_cache
