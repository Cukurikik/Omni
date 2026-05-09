"""
omni_positional_encoding.py — Positional Encoding Library
Inspired by: Transformer position encoding variants from Memformer/TVLT
Layer: Compute / AI

Comprehensive positional encoding library with sinusoidal, learned,
relative, ALiBi, and 2D spatial encodings for vision-language models.
"""

import torch
import torch.nn as nn
import math
from typing import Optional, Tuple


class SinusoidalEncoding(nn.Module):
    """Classic sinusoidal positional encoding from 'Attention Is All You Need'."""

    def __init__(self, dim: int, max_len: int = 8192, base: float = 10000.0):
        super().__init__()
        pe = torch.zeros(max_len, dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, dim, 2).float() * (-math.log(base) / dim))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.shape[1]]


class LearnedEncoding(nn.Module):
    """Learned positional embeddings with initialization strategy."""

    def __init__(self, dim: int, max_len: int = 2048):
        super().__init__()
        self.embedding = nn.Embedding(max_len, dim)
        nn.init.trunc_normal_(self.embedding.weight, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        positions = torch.arange(x.shape[1], device=x.device)
        return x + self.embedding(positions)


class RotaryPositionEncoding(nn.Module):
    """Rotary Position Embedding (RoPE) with NTK-aware dynamic scaling."""

    def __init__(self, dim: int, max_len: int = 8192, base: float = 10000.0,
                 scaling_factor: float = 1.0):
        super().__init__()
        self.dim = dim
        self.max_len = max_len
        self.base = base
        self.scaling_factor = scaling_factor

        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self._build_cache(max_len)

    def _build_cache(self, max_len: int):
        t = torch.arange(max_len, dtype=self.inv_freq.dtype, device=self.inv_freq.device)
        t = t / self.scaling_factor

        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)

        self.register_buffer("cos_cached", emb.cos().unsqueeze(0).unsqueeze(0))
        self.register_buffer("sin_cached", emb.sin().unsqueeze(0).unsqueeze(0))

    @staticmethod
    def _rotate_half(x: torch.Tensor) -> torch.Tensor:
        x1 = x[..., :x.shape[-1] // 2]
        x2 = x[..., x.shape[-1] // 2:]
        return torch.cat((-x2, x1), dim=-1)

    def forward(self, q: torch.Tensor, k: torch.Tensor,
                offset: int = 0) -> Tuple[torch.Tensor, torch.Tensor]:
        seq_len = q.shape[2]
        cos = self.cos_cached[:, :, offset:offset + seq_len]
        sin = self.sin_cached[:, :, offset:offset + seq_len]

        q_rot = q * cos + self._rotate_half(q) * sin
        k_rot = k * cos + self._rotate_half(k) * sin
        return q_rot, k_rot


class ALiBiEncoding(nn.Module):
    """Attention with Linear Biases — position-free extrapolation.

    Adds linear distance-based biases directly to attention scores,
    enabling length generalization without position embeddings.
    """

    def __init__(self, num_heads: int):
        super().__init__()
        self.num_heads = num_heads

        slopes = self._compute_slopes(num_heads)
        self.register_buffer("slopes", slopes)

    @staticmethod
    def _compute_slopes(num_heads: int) -> torch.Tensor:
        """Compute ALiBi slopes using geometric sequence."""
        def get_slopes_power_of_2(n):
            start = 2 ** (-(2 ** -(math.log2(n) - 3)))
            ratio = start
            return [start * ratio ** i for i in range(n)]

        if math.log2(num_heads).is_integer():
            slopes = get_slopes_power_of_2(num_heads)
        else:
            closest_pow2 = 2 ** math.floor(math.log2(num_heads))
            slopes = get_slopes_power_of_2(closest_pow2)
            extra = get_slopes_power_of_2(2 * closest_pow2)
            slopes.extend(extra[0::2][:num_heads - closest_pow2])

        return torch.tensor(slopes, dtype=torch.float32).unsqueeze(0).unsqueeze(-1).unsqueeze(-1)

    def forward(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Generate ALiBi bias matrix for given sequence length."""
        positions = torch.arange(seq_len, device=device)
        distance = positions.unsqueeze(0) - positions.unsqueeze(1)
        bias = distance.unsqueeze(0).unsqueeze(0) * self.slopes.to(device)
        return bias


class SpatialEncoding2D(nn.Module):
    """2D spatial positional encoding for image patches.

    Encodes row and column positions separately and combines
    them, suitable for ViT-style patch embeddings.
    """

    def __init__(self, dim: int, max_h: int = 64, max_w: int = 64):
        super().__init__()
        self.row_embed = nn.Embedding(max_h, dim // 2)
        self.col_embed = nn.Embedding(max_w, dim // 2)
        nn.init.trunc_normal_(self.row_embed.weight, std=0.02)
        nn.init.trunc_normal_(self.col_embed.weight, std=0.02)

    def forward(self, x: torch.Tensor, h: int, w: int) -> torch.Tensor:
        """Add 2D position encodings.

        Args:
            x: (B, h*w, D) patch embeddings
            h: number of rows (patches)
            w: number of columns (patches)
        """
        rows = torch.arange(h, device=x.device).unsqueeze(1).expand(h, w).reshape(-1)
        cols = torch.arange(w, device=x.device).unsqueeze(0).expand(h, w).reshape(-1)

        row_enc = self.row_embed(rows)
        col_enc = self.col_embed(cols)
        pos = torch.cat([row_enc, col_enc], dim=-1)

        return x + pos.unsqueeze(0)


class TemporalEncoding(nn.Module):
    """Temporal positional encoding for video/audio frames.

    Combines frame-level temporal encoding with optional
    modality-specific embeddings.
    """

    def __init__(self, dim: int, max_frames: int = 256):
        super().__init__()
        self.temporal_embed = nn.Embedding(max_frames, dim)
        self.modality_embed = nn.ParameterDict({
            "video": nn.Parameter(torch.randn(dim) * 0.02),
            "audio": nn.Parameter(torch.randn(dim) * 0.02),
        })
        nn.init.trunc_normal_(self.temporal_embed.weight, std=0.02)

    def forward(self, x: torch.Tensor, modality: str = "video") -> torch.Tensor:
        B, T, D = x.shape
        positions = torch.arange(T, device=x.device)
        temporal = self.temporal_embed(positions)

        modality_bias = self.modality_embed.get(modality, torch.zeros(D, device=x.device))
        return x + temporal.unsqueeze(0) + modality_bias


class OmniPositionalEncoding(nn.Module):
    """Unified positional encoding module supporting multiple strategies."""

    STRATEGIES = {
        "sinusoidal", "learned", "rotary", "alibi", "spatial_2d", "temporal", "none"
    }

    def __init__(self, dim: int, strategy: str = "rotary",
                 max_len: int = 8192, num_heads: int = 8, **kwargs):
        super().__init__()
        assert strategy in self.STRATEGIES, f"Unknown strategy: {strategy}"
        self.strategy = strategy

        if strategy == "sinusoidal":
            self.encoding = SinusoidalEncoding(dim, max_len)
        elif strategy == "learned":
            self.encoding = LearnedEncoding(dim, max_len)
        elif strategy == "rotary":
            head_dim = dim // num_heads
            self.encoding = RotaryPositionEncoding(head_dim, max_len)
        elif strategy == "alibi":
            self.encoding = ALiBiEncoding(num_heads)
        elif strategy == "spatial_2d":
            self.encoding = SpatialEncoding2D(dim)
        elif strategy == "temporal":
            self.encoding = TemporalEncoding(dim, max_len)
        else:
            self.encoding = nn.Identity()

    def forward(self, x: torch.Tensor, **kwargs) -> torch.Tensor:
        if self.strategy in ("sinusoidal", "learned"):
            return self.encoding(x)
        elif self.strategy == "spatial_2d":
            h = kwargs.get("h", int(x.shape[1] ** 0.5))
            w = kwargs.get("w", int(x.shape[1] ** 0.5))
            return self.encoding(x, h, w)
        elif self.strategy == "temporal":
            modality = kwargs.get("modality", "video")
            return self.encoding(x, modality)
        return x
