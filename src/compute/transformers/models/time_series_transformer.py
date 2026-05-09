"""
OMNI Transformer — Time-Series Transformer
For biosignal, financial, and sensor data.
Learned from: harryjdavies/HeartGPT, ai4co/parco
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..core import TransformerEncoderBlock, AttentionType, NormType, FFNActivation


@dataclass
class TimeSeriesConfig:
    input_dim: int = 1
    embed_dim: int = 256
    num_layers: int = 6
    num_heads: int = 8
    ffn_dim: int = 1024
    max_seq_len: int = 2048
    num_classes: int = 5  # For classification tasks
    dropout: float = 0.1
    forecast_horizon: int = 96
    task: str = "classification"  # "classification", "forecasting", "anomaly"


class TimeSeriesPatchEmbed(nn.Module):
    """Embed time-series patches into latent space."""
    def __init__(self, input_dim: int, embed_dim: int, patch_len: int = 16, stride: int = 8):
        super().__init__()
        self.patch_len = patch_len
        self.stride = stride
        self.proj = nn.Linear(input_dim * patch_len, embed_dim)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, S, C) -> patches
        B, S, C = x.shape
        patches = x.unfold(dimension=1, size=self.patch_len, step=self.stride)  # (B, num_patches, C, patch_len)
        patches = patches.reshape(B, patches.size(1), -1)  # (B, num_patches, C*patch_len)
        return self.norm(self.proj(patches))


class OmniTimeSeriesTransformer(nn.Module):
    """Production transformer for time-series analysis."""
    def __init__(self, config: TimeSeriesConfig):
        super().__init__()
        self.config = config
        self.input_proj = nn.Linear(config.input_dim, config.embed_dim)
        self.pos_embed = nn.Embedding(config.max_seq_len, config.embed_dim)
        self.dropout = nn.Dropout(config.dropout)

        self.encoder = nn.ModuleList([
            TransformerEncoderBlock(
                embed_dim=config.embed_dim, num_heads=config.num_heads,
                ffn_dim=config.ffn_dim, dropout=config.dropout,
                activation=FFNActivation.GELU, norm_type=NormType.LAYER_NORM,
                attention_type=AttentionType.STANDARD, use_rope=False,
            ) for _ in range(config.num_layers)
        ])
        self.norm = nn.LayerNorm(config.embed_dim)

        if config.task == "classification":
            self.head = nn.Sequential(
                nn.Linear(config.embed_dim, config.embed_dim // 2),
                nn.GELU(), nn.Dropout(config.dropout),
                nn.Linear(config.embed_dim // 2, config.num_classes),
            )
        elif config.task == "forecasting":
            self.head = nn.Linear(config.embed_dim, config.forecast_horizon * config.input_dim)
        else:  # anomaly detection
            self.head = nn.Sequential(
                nn.Linear(config.embed_dim, config.embed_dim // 2),
                nn.GELU(), nn.Linear(config.embed_dim // 2, 1), nn.Sigmoid(),
            )

    def forward(self, x: torch.Tensor, labels: Optional[torch.Tensor] = None) -> dict:
        B, S, C = x.shape
        hidden = self.input_proj(x)
        positions = torch.arange(S, device=x.device).unsqueeze(0)
        hidden = self.dropout(hidden + self.pos_embed(positions))

        for layer in self.encoder:
            hidden = layer(hidden)
        hidden = self.norm(hidden)

        if self.config.task == "classification":
            pooled = hidden.mean(dim=1)
            logits = self.head(pooled)
            loss = F.cross_entropy(logits, labels) if labels is not None else None
        elif self.config.task == "forecasting":
            logits = self.head(hidden[:, -1]).view(B, self.config.forecast_horizon, self.config.input_dim)
            loss = F.mse_loss(logits, labels) if labels is not None else None
        else:
            logits = self.head(hidden).squeeze(-1)
            loss = F.binary_cross_entropy(logits, labels.float()) if labels is not None else None

        return {"logits": logits, "loss": loss, "hidden_states": hidden}
