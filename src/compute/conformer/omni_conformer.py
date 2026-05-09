"""
omni_conformer.py — Conformer Block for Audio Processing
Inspired by: SoundStorm Conformer backbone
Layer: Compute / AI

Combines convolution and self-attention for speech/audio modeling.
Used as the backbone in SoundStorm and speech recognition pipelines.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class ConformerConvolution(nn.Module):
    """Depthwise separable convolution with gating."""

    def __init__(self, dim: int, kernel_size: int = 31, expansion: int = 2):
        super().__init__()
        inner_dim = dim * expansion
        padding = (kernel_size - 1) // 2
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, inner_dim * 2),
            nn.GLU(dim=-1),
            nn.Conv1d(inner_dim, inner_dim, kernel_size, padding=padding, groups=inner_dim),
            nn.BatchNorm1d(inner_dim),
            nn.SiLU(),
            nn.Linear(inner_dim, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = self.net[0](x)  # LayerNorm
        x = self.net[1](x)  # Linear -> 2*inner
        x = self.net[2](x)  # GLU -> inner
        x = x.transpose(1, 2)  # (B, C, T) for Conv1d
        x = self.net[3](x)  # Depthwise conv
        x = self.net[4](x)  # BatchNorm
        x = self.net[5](x)  # SiLU
        x = x.transpose(1, 2)  # (B, T, C)
        x = self.net[6](x)  # Linear -> dim
        return residual + x


class ConformerFeedForward(nn.Module):
    """Macaron-style feed-forward with pre-norm."""

    def __init__(self, dim: int, mult: int = 4, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * mult),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(dim * mult, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + 0.5 * self.net(x)


class ConformerAttention(nn.Module):
    """Multi-head self-attention with relative positional encoding."""

    def __init__(self, dim: int, heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(
            dim, heads, dropout=dropout, batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        normed = self.norm(x)
        attn_out, _ = self.attn(normed, normed, normed, key_padding_mask=mask)
        return x + self.dropout(attn_out)


class ConformerBlock(nn.Module):
    """Single Conformer block: FF → Attn → Conv → FF."""

    def __init__(self, dim: int = 512, heads: int = 8,
                 conv_kernel: int = 31, ff_mult: int = 4,
                 dropout: float = 0.1):
        super().__init__()
        self.ff1 = ConformerFeedForward(dim, ff_mult, dropout)
        self.attn = ConformerAttention(dim, heads, dropout)
        self.conv = ConformerConvolution(dim, conv_kernel)
        self.ff2 = ConformerFeedForward(dim, ff_mult, dropout)
        self.post_norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = self.ff1(x)
        x = self.attn(x, mask)
        x = self.conv(x)
        x = self.ff2(x)
        x = self.post_norm(x)
        return x


class OmniConformer(nn.Module):
    """Full Conformer encoder stack for audio processing.

    Used as backbone in SoundStorm for neural audio generation.
    """

    def __init__(self, dim: int = 512, depth: int = 12, heads: int = 8,
                 conv_kernel: int = 31, ff_mult: int = 4,
                 input_dim: int = 128, dropout: float = 0.1):
        super().__init__()
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, dim),
            nn.LayerNorm(dim),
            nn.Dropout(dropout),
        )
        self.pos_embed = nn.Parameter(torch.randn(1, 4096, dim) * 0.02)
        self.blocks = nn.ModuleList([
            ConformerBlock(dim, heads, conv_kernel, ff_mult, dropout)
            for _ in range(depth)
        ])
        self.output_norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = self.input_proj(x)
        seq_len = x.shape[1]
        x = x + self.pos_embed[:, :seq_len]
        for block in self.blocks:
            x = block(x, mask)
        return self.output_norm(x)
