"""
omni_feature_extractor.py — Multi-Scale Feature Extraction Pipeline
Inspired by: TVLT multi-patch + FashionCLIP feature extraction
Layer: Compute / AI

Extracts features at multiple spatial scales and temporal resolutions
for multimodal transformer inputs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ScaleConfig:
    spatial_scales: List[int] = None
    temporal_scales: List[int] = None

    def __post_init__(self):
        if self.spatial_scales is None:
            self.spatial_scales = [7, 14, 28]
        if self.temporal_scales is None:
            self.temporal_scales = [8, 16, 32]


class SpatialPyramidPooling(nn.Module):
    """Extract features at multiple spatial resolutions."""

    def __init__(self, in_channels: int, out_dim: int, scales: List[int]):
        super().__init__()
        self.scales = scales
        self.projectors = nn.ModuleList([
            nn.Sequential(
                nn.AdaptiveAvgPool2d(s),
                nn.Flatten(2),
                nn.Linear(in_channels * s * s, out_dim),
                nn.LayerNorm(out_dim),
                nn.GELU(),
            )
            for s in scales
        ])
        self.fusion = nn.Linear(out_dim * len(scales), out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        features = []
        for proj in self.projectors:
            f = proj(x)
            features.append(f)
        concat = torch.cat(features, dim=-1)
        return self.fusion(concat)


class TemporalPooling(nn.Module):
    """Multi-scale temporal feature aggregation for sequences."""

    def __init__(self, dim: int, scales: List[int]):
        super().__init__()
        self.scales = scales
        self.conv_pools = nn.ModuleList([
            nn.Sequential(
                nn.Conv1d(dim, dim, kernel_size=s, stride=s, groups=dim),
                nn.BatchNorm1d(dim),
                nn.GELU(),
            )
            for s in scales
        ])
        self.fusion = nn.Sequential(
            nn.Linear(dim * len(scales), dim),
            nn.LayerNorm(dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, D)
        x_t = x.transpose(1, 2)  # (B, D, T)
        pooled = []
        for conv in self.conv_pools:
            if x_t.shape[2] >= conv[0].kernel_size[0]:
                p = conv(x_t).mean(dim=2)
            else:
                p = x_t.mean(dim=2)
            pooled.append(p)
        concat = torch.cat(pooled, dim=-1)
        return self.fusion(concat)


class AudioFeatureExtractor(nn.Module):
    """Extract features from raw audio or mel-spectrograms."""

    def __init__(self, input_dim: int = 128, hidden_dim: int = 512,
                 output_dim: int = 768, num_layers: int = 3):
        super().__init__()
        layers = []
        for i in range(num_layers):
            in_d = input_dim if i == 0 else hidden_dim
            out_d = output_dim if i == num_layers - 1 else hidden_dim
            layers.extend([
                nn.Conv1d(in_d, out_d, kernel_size=3, padding=1),
                nn.BatchNorm1d(out_d),
                nn.GELU(),
                nn.MaxPool1d(2) if i < num_layers - 1 else nn.Identity(),
            ])
        self.net = nn.Sequential(*layers)
        self.output_norm = nn.LayerNorm(output_dim)

    def forward(self, mel_spec: torch.Tensor) -> torch.Tensor:
        # mel_spec: (B, F, T) where F=mel bins, T=time
        x = self.net(mel_spec)
        x = x.transpose(1, 2)  # (B, T', D)
        return self.output_norm(x)


class ImageFeatureExtractor(nn.Module):
    """CNN-based image feature extractor with multi-scale output."""

    def __init__(self, in_channels: int = 3, dims: List[int] = None,
                 output_dim: int = 768):
        super().__init__()
        if dims is None:
            dims = [64, 128, 256, 512]

        stages = []
        for i, d in enumerate(dims):
            in_c = in_channels if i == 0 else dims[i - 1]
            stages.append(nn.Sequential(
                nn.Conv2d(in_c, d, 3, stride=2, padding=1),
                nn.BatchNorm2d(d),
                nn.GELU(),
                nn.Conv2d(d, d, 3, padding=1),
                nn.BatchNorm2d(d),
                nn.GELU(),
            ))
        self.stages = nn.ModuleList(stages)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.proj = nn.Sequential(
            nn.Flatten(),
            nn.Linear(dims[-1], output_dim),
            nn.LayerNorm(output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for stage in self.stages:
            x = stage(x)
        x = self.pool(x)
        return self.proj(x)

    def forward_multiscale(self, x: torch.Tensor) -> List[torch.Tensor]:
        features = []
        for stage in self.stages:
            x = stage(x)
            features.append(x)
        return features


class OmniFeatureExtractor(nn.Module):
    """Unified multi-modal feature extraction pipeline.

    Supports image, audio, and text feature extraction
    with multi-scale spatial and temporal pooling.
    """

    def __init__(self, output_dim: int = 768, config: ScaleConfig = None):
        super().__init__()
        if config is None:
            config = ScaleConfig()

        self.image_extractor = ImageFeatureExtractor(output_dim=output_dim)
        self.audio_extractor = AudioFeatureExtractor(output_dim=output_dim)
        self.temporal_pool = TemporalPooling(output_dim, config.temporal_scales)

        self.modality_embeds = nn.ParameterDict({
            "image": nn.Parameter(torch.randn(output_dim) * 0.02),
            "audio": nn.Parameter(torch.randn(output_dim) * 0.02),
            "text": nn.Parameter(torch.randn(output_dim) * 0.02),
        })

    def extract_image(self, images: torch.Tensor) -> torch.Tensor:
        feat = self.image_extractor(images)
        return feat + self.modality_embeds["image"]

    def extract_audio(self, mel_spec: torch.Tensor) -> torch.Tensor:
        feat = self.audio_extractor(mel_spec)
        return feat + self.modality_embeds["audio"]

    def extract_temporal(self, sequence: torch.Tensor) -> torch.Tensor:
        return self.temporal_pool(sequence)

    def forward(self, images: Optional[torch.Tensor] = None,
                audio: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        result = {}
        if images is not None:
            result["image"] = self.extract_image(images)
        if audio is not None:
            result["audio"] = self.extract_audio(audio)
            result["audio_temporal"] = self.extract_temporal(result["audio"])
        return result
