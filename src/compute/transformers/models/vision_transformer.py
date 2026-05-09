"""
OMNI Transformer — Vision Transformer (ViT)
Production implementation for image classification.
Learned from: YilmazKadir/Volt, RLado/STB-VMM, google/vit-base-patch16-224
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import torch
import torch.nn as nn
from ..core import TransformerEncoderBlock, AttentionType, NormType, FFNActivation


@dataclass
class ViTConfig:
    image_size: int = 224
    patch_size: int = 16
    in_channels: int = 3
    embed_dim: int = 768
    num_layers: int = 12
    num_heads: int = 12
    ffn_dim: int = 3072
    num_classes: int = 1000
    dropout: float = 0.1
    attention_dropout: float = 0.0


class PatchEmbedding(nn.Module):
    """Convert image into patch embeddings via convolution."""
    def __init__(self, config: ViTConfig):
        super().__init__()
        self.num_patches = (config.image_size // config.patch_size) ** 2
        self.proj = nn.Conv2d(
            config.in_channels, config.embed_dim,
            kernel_size=config.patch_size, stride=config.patch_size,
        )
        self.cls_token = nn.Parameter(torch.randn(1, 1, config.embed_dim) * 0.02)
        self.pos_embed = nn.Parameter(
            torch.randn(1, self.num_patches + 1, config.embed_dim) * 0.02
        )
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        x = self.proj(x).flatten(2).transpose(1, 2)  # (B, num_patches, D)
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos_embed
        return self.dropout(x)


class OmniViT(nn.Module):
    """Production Vision Transformer for image classification."""
    def __init__(self, config: ViTConfig):
        super().__init__()
        self.config = config
        self.patch_embed = PatchEmbedding(config)
        self.encoder = nn.ModuleList([
            TransformerEncoderBlock(
                embed_dim=config.embed_dim,
                num_heads=config.num_heads,
                ffn_dim=config.ffn_dim,
                dropout=config.dropout,
                attention_dropout=config.attention_dropout,
                activation=FFNActivation.GELU,
                norm_type=NormType.LAYER_NORM,
                attention_type=AttentionType.STANDARD,
                use_rope=False,
            ) for _ in range(config.num_layers)
        ])
        self.norm = nn.LayerNorm(config.embed_dim)
        self.head = nn.Linear(config.embed_dim, config.num_classes)
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m):
        if isinstance(m, nn.Linear):
            nn.init.trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, pixel_values: torch.Tensor, labels: Optional[torch.Tensor] = None) -> dict:
        x = self.patch_embed(pixel_values)
        for layer in self.encoder:
            x = layer(x)
        x = self.norm(x)
        cls_output = x[:, 0]
        logits = self.head(cls_output)
        loss = None
        if labels is not None:
            loss = nn.functional.cross_entropy(logits, labels)
        return {"logits": logits, "loss": loss, "cls_embedding": cls_output}
