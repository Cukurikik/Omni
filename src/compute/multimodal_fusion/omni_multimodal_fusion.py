"""
omni_multimodal_fusion.py — Cross-Modal Gated Fusion Transformer
Inspired by: TVLT multimodal encoder + FashionCLIP dual-encoder
Layer: Compute / AI

Fuses vision, audio, and text modalities via gated cross-attention
for joint multimodal understanding.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional


class GatedCrossAttention(nn.Module):
    """Cross-attention with learned gating for selective modality fusion."""

    def __init__(self, dim: int = 512, heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.gate = nn.Sequential(nn.Linear(dim, dim), nn.Sigmoid())
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, dim * 4), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(dim * 4, dim), nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor, context: torch.Tensor) -> torch.Tensor:
        normed = self.norm1(x)
        attn_out, _ = self.attn(normed, context, context)
        x = x + self.gate(attn_out) * attn_out
        x = x + self.ff(self.norm2(x))
        return x


class ModalityProjector(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, num_layers: int = 2):
        super().__init__()
        layers = []
        for i in range(num_layers):
            d_in = in_dim if i == 0 else out_dim
            layers.extend([nn.Linear(d_in, out_dim), nn.GELU(), nn.LayerNorm(out_dim)])
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class OmniMultimodalFusion(nn.Module):
    """Three-way multimodal fusion with gated cross-attention.

    Supports any combination of vision, audio, and text modalities.
    Uses bidirectional cross-attention between modality pairs.
    """

    def __init__(self, vision_dim: int = 768, audio_dim: int = 512,
                 text_dim: int = 768, fusion_dim: int = 512,
                 depth: int = 4, heads: int = 8):
        super().__init__()
        self.vision_proj = ModalityProjector(vision_dim, fusion_dim)
        self.audio_proj = ModalityProjector(audio_dim, fusion_dim)
        self.text_proj = ModalityProjector(text_dim, fusion_dim)

        self.cross_v2a = nn.ModuleList([GatedCrossAttention(fusion_dim, heads) for _ in range(depth)])
        self.cross_a2v = nn.ModuleList([GatedCrossAttention(fusion_dim, heads) for _ in range(depth)])
        self.cross_t2va = nn.ModuleList([GatedCrossAttention(fusion_dim, heads) for _ in range(depth)])

        self.fusion_norm = nn.LayerNorm(fusion_dim)
        self.fusion_head = nn.Linear(fusion_dim, fusion_dim)

    def forward(self, vision: Optional[torch.Tensor] = None,
                audio: Optional[torch.Tensor] = None,
                text: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        features = {}
        if vision is not None:
            features["vision"] = self.vision_proj(vision)
        if audio is not None:
            features["audio"] = self.audio_proj(audio)
        if text is not None:
            features["text"] = self.text_proj(text)

        if "vision" in features and "audio" in features:
            v, a = features["vision"], features["audio"]
            for cv2a, ca2v in zip(self.cross_v2a, self.cross_a2v):
                v_new = cv2a(v, a)
                a_new = ca2v(a, v)
                v, a = v_new, a_new
            features["vision"], features["audio"] = v, a

        if "text" in features and len(features) > 1:
            ctx_keys = [k for k in features if k != "text"]
            ctx = torch.cat([features[k] for k in ctx_keys], dim=1)
            t = features["text"]
            for cross in self.cross_t2va:
                t = cross(t, ctx)
            features["text"] = t

        pooled = [f.mean(dim=1) for f in features.values()]
        fused = torch.stack(pooled, dim=0).mean(dim=0)
        fused = self.fusion_head(self.fusion_norm(fused))
        return {"fused": fused, "modality_features": features}
