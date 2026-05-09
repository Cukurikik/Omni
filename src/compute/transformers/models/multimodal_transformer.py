"""
OMNI Transformer — Multimodal Fusion Transformer
Text + Image fusion for VQA, captioning, and multimodal understanding.
Learned from: Volt, CLIP patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class MultimodalConfig:
    text_dim: int = 768
    image_dim: int = 768
    fusion_dim: int = 512
    num_layers: int = 4
    num_heads: int = 8
    ffn_dim: int = 2048
    num_classes: int = 3129  # VQA answer vocabulary
    dropout: float = 0.1


class CrossModalAttention(nn.Module):
    """Cross-modal attention between text and image features."""
    def __init__(self, dim: int, num_heads: int, dropout: float = 0.0):
        super().__init__()
        self.mha = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.norm = nn.LayerNorm(dim)

    def forward(self, query: torch.Tensor, context: torch.Tensor) -> torch.Tensor:
        attn_out, _ = self.mha(query, context, context)
        return self.norm(query + attn_out)


class OmniMultimodalTransformer(nn.Module):
    """Production multimodal transformer for vision-language tasks."""
    def __init__(self, config: MultimodalConfig):
        super().__init__()
        self.text_proj = nn.Linear(config.text_dim, config.fusion_dim)
        self.image_proj = nn.Linear(config.image_dim, config.fusion_dim)

        self.text_to_image_layers = nn.ModuleList([
            CrossModalAttention(config.fusion_dim, config.num_heads, config.dropout)
            for _ in range(config.num_layers)
        ])
        self.image_to_text_layers = nn.ModuleList([
            CrossModalAttention(config.fusion_dim, config.num_heads, config.dropout)
            for _ in range(config.num_layers)
        ])

        self.fusion = nn.Sequential(
            nn.Linear(config.fusion_dim * 2, config.fusion_dim),
            nn.GELU(),
            nn.Dropout(config.dropout),
        )
        self.classifier = nn.Linear(config.fusion_dim, config.num_classes)

    def forward(self, text_features: torch.Tensor, image_features: torch.Tensor,
                labels: Optional[torch.Tensor] = None) -> Dict:
        text_proj = self.text_proj(text_features)
        image_proj = self.image_proj(image_features)

        for t2i, i2t in zip(self.text_to_image_layers, self.image_to_text_layers):
            text_proj = t2i(text_proj, image_proj)
            image_proj = i2t(image_proj, text_proj)

        text_pooled = text_proj.mean(dim=1)
        image_pooled = image_proj.mean(dim=1)
        fused = self.fusion(torch.cat([text_pooled, image_pooled], dim=-1))
        logits = self.classifier(fused)

        loss = None
        if labels is not None:
            loss = F.cross_entropy(logits, labels)
        return {"logits": logits, "loss": loss, "fused_features": fused}
