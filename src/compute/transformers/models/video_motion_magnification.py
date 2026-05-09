"""
OMNI Transformer — Video Motion Magnification Transformer
Spatio-temporal transformer for sub-pixel motion amplification.
Learned from: RLado/STB-VMM (video motion magnification)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class VMMConfig:
    in_channels: int = 3
    embed_dim: int = 64
    num_layers: int = 4
    num_heads: int = 4
    temporal_window: int = 16
    spatial_size: int = 64
    amplification_factor: float = 10.0


class SpatioTemporalPatchEmbed(nn.Module):
    """3D patch embedding for video sequences."""
    def __init__(self, in_channels: int, embed_dim: int, patch_size: Tuple[int, int, int] = (2, 4, 4)):
        super().__init__()
        self.proj = nn.Conv3d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T, H, W)
        x = self.proj(x)  # (B, D, T', H', W')
        B, D, T, H, W = x.shape
        x = x.flatten(2).transpose(1, 2)  # (B, T'*H'*W', D)
        return self.norm(x)


class MotionEncoder(nn.Module):
    """Encode subtle motion signals from video frames."""
    def __init__(self, config: VMMConfig):
        super().__init__()
        self.embed = SpatioTemporalPatchEmbed(config.in_channels, config.embed_dim)
        self.layers = nn.ModuleList()
        for _ in range(config.num_layers):
            self.layers.append(nn.TransformerEncoderLayer(
                d_model=config.embed_dim, nhead=config.num_heads,
                dim_feedforward=config.embed_dim * 4, dropout=0.1, batch_first=True,
            ))

    def forward(self, video: torch.Tensor) -> torch.Tensor:
        x = self.embed(video)
        for layer in self.layers:
            x = layer(x)
        return x


class MotionAmplifier(nn.Module):
    """Amplify detected motion signals."""
    def __init__(self, config: VMMConfig):
        super().__init__()
        self.amp_factor = config.amplification_factor
        self.motion_filter = nn.Sequential(
            nn.Linear(config.embed_dim, config.embed_dim),
            nn.ReLU(),
            nn.Linear(config.embed_dim, config.embed_dim),
            nn.Sigmoid(),
        )
        self.reconstruction = nn.Sequential(
            nn.Linear(config.embed_dim, config.embed_dim * 4),
            nn.GELU(),
            nn.Linear(config.embed_dim * 4, config.in_channels * 16),
        )

    def forward(self, motion_features: torch.Tensor, reference_features: torch.Tensor) -> torch.Tensor:
        # Compute motion residual
        motion_diff = motion_features - reference_features
        # Temporal bandpass filter
        motion_mask = self.motion_filter(motion_diff)
        # Amplify
        amplified = reference_features + motion_diff * motion_mask * self.amp_factor
        return self.reconstruction(amplified)


class OmniVMM(nn.Module):
    """Production video motion magnification transformer."""
    def __init__(self, config: VMMConfig):
        super().__init__()
        self.encoder = MotionEncoder(config)
        self.amplifier = MotionAmplifier(config)
        self.config = config

    def forward(self, video: torch.Tensor) -> Dict:
        # video: (B, C, T, H, W)
        features = self.encoder(video)
        # Use first frame as reference
        B, N, D = features.shape
        T_patches = N // (self.config.spatial_size // 4) ** 2
        ref_features = features[:, :N // T_patches].expand_as(features[:, :N // T_patches])
        amplified = self.amplifier(features, ref_features.expand(-1, features.size(1), -1))
        return {"amplified_output": amplified, "motion_features": features}
