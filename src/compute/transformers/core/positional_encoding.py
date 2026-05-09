"""
OMNI Transformer Engine — Positional Encoding Module
Sinusoidal, Learnable, ALiBi, and Relative Position Bias.
Learned from: Vaswani et al., PRESS (ALiBi), retarfi/language-pretraining
"""
import math
from enum import Enum, auto
from typing import Optional
import torch
import torch.nn as nn


class PositionEncodingType(Enum):
    SINUSOIDAL = auto()
    LEARNABLE = auto()
    ALIBI = auto()
    RELATIVE_BIAS = auto()


class SinusoidalPositionalEncoding(nn.Module):
    """Fixed sinusoidal PE from Attention Is All You Need."""
    def __init__(self, embed_dim: int, max_seq_len: int = 8192, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_seq_len, embed_dim)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, embed_dim, 2).float() * (-math.log(10000.0) / embed_dim))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0), persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(x + self.pe[:, :x.size(1), :])


class LearnablePositionalEncoding(nn.Module):
    """Learnable positional embeddings (BERT, GPT-2 style)."""
    def __init__(self, embed_dim: int, max_seq_len: int = 8192, dropout: float = 0.1):
        super().__init__()
        self.position_embeddings = nn.Embedding(max_seq_len, embed_dim)
        self.dropout = nn.Dropout(p=dropout)
        nn.init.normal_(self.position_embeddings.weight, mean=0.0, std=0.02)

    def forward(self, x: torch.Tensor, position_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        if position_ids is None:
            position_ids = torch.arange(x.size(1), device=x.device).unsqueeze(0)
        return self.dropout(x + self.position_embeddings(position_ids))


class ALiBiPositionalBias(nn.Module):
    """Attention with Linear Biases — no position embeddings, bias in attn scores."""
    def __init__(self, num_heads: int, max_seq_len: int = 8192):
        super().__init__()
        self.num_heads = num_heads
        slopes = self._compute_slopes(num_heads)
        self.register_buffer("slopes", slopes, persistent=False)
        self._build_cache(max_seq_len)

    @staticmethod
    def _compute_slopes(n: int) -> torch.Tensor:
        def _power_of_2(n):
            start = 2 ** (-(2 ** -(math.log2(n) - 3)))
            return [start * (start ** i) for i in range(n)]
        if math.log2(n).is_integer():
            return torch.tensor(_power_of_2(n), dtype=torch.float32)
        cp = 2 ** math.floor(math.log2(n))
        return torch.tensor(_power_of_2(cp) + _power_of_2(2 * cp)[0::2][:n - cp], dtype=torch.float32)

    def _build_cache(self, max_len: int) -> None:
        pos = torch.arange(max_len)
        rel = (pos.unsqueeze(0) - pos.unsqueeze(1)).abs().float().neg()
        self.register_buffer("alibi_bias", rel.unsqueeze(0) * self.slopes.unsqueeze(-1).unsqueeze(-1), persistent=False)

    def forward(self, seq_len_q: int, seq_len_k: int) -> torch.Tensor:
        if seq_len_k > self.alibi_bias.size(-1):
            self._build_cache(seq_len_k)
        return self.alibi_bias[:, :seq_len_q, :seq_len_k]


class RelativePositionBias(nn.Module):
    """T5-style relative position bias."""
    def __init__(self, num_heads: int, num_buckets: int = 32, max_distance: int = 128):
        super().__init__()
        self.num_buckets = num_buckets
        self.max_distance = max_distance
        self.relative_attention_bias = nn.Embedding(num_buckets, num_heads)

    def forward(self, seq_len_q: int, seq_len_k: int, device: torch.device) -> torch.Tensor:
        q_pos = torch.arange(seq_len_q, device=device)
        k_pos = torch.arange(seq_len_k, device=device)
        rel = k_pos.unsqueeze(0) - q_pos.unsqueeze(1)
        buckets = self._bucket(rel)
        return self.relative_attention_bias(buckets).permute(2, 0, 1).unsqueeze(0)

    def _bucket(self, rel: torch.Tensor) -> torch.Tensor:
        nb = self.num_buckets // 2
        ret = (rel > 0).long() * nb
        n = rel.abs()
        max_exact = nb // 2
        is_small = n < max_exact
        large = max_exact + (torch.log(n.float() / max_exact) / math.log(self.max_distance / max_exact) * (nb - max_exact)).long()
        return ret + torch.where(is_small, n, large.clamp(max=nb - 1))
