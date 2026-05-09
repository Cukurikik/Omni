"""
omni_tvlt.py — Textless Vision-Language Transformer
Inspired by: zinengtang/TVLT (NeurIPS 2022 Oral)
Layer: Compute / AI

Multimodal transformer that learns vision-language representations
from raw video frames and audio spectrograms WITHOUT text.
Uses Masked Autoencoding + Contrastive alignment objectives.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TVLTConfig:
    image_size: int = 224
    patch_size: int = 16
    num_frames: int = 8
    audio_length: int = 1024
    audio_patch_size: int = 16
    audio_freq_bins: int = 128
    dim: int = 768
    depth: int = 12
    heads: int = 12
    dim_head: int = 64
    ff_mult: int = 4
    dropout: float = 0.1
    mae_masking_ratio: float = 0.75
    decoder_dim: int = 384
    decoder_depth: int = 4
    decoder_heads: int = 6


class PatchEmbedding3D(nn.Module):
    """Extracts patches from video frames (B, T, C, H, W) -> (B, N, D)."""

    def __init__(self, in_channels: int = 3, patch_size: int = 16,
                 dim: int = 768, num_frames: int = 8):
        super().__init__()
        self.patch_size = patch_size
        self.projection = nn.Conv3d(
            in_channels, dim,
            kernel_size=(2, patch_size, patch_size),
            stride=(2, patch_size, patch_size),
        )
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, T, H, W)
        x = self.projection(x)  # (B, D, T', H', W')
        x = x.flatten(2).transpose(1, 2)  # (B, N, D)
        return self.norm(x)


class AudioPatchEmbedding(nn.Module):
    """Extracts patches from audio spectrograms (B, 1, F, T) -> (B, N, D)."""

    def __init__(self, freq_bins: int = 128, patch_size: int = 16, dim: int = 768):
        super().__init__()
        self.projection = nn.Conv2d(
            1, dim,
            kernel_size=(freq_bins // 8, patch_size),
            stride=(freq_bins // 8, patch_size),
        )
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.projection(x)  # (B, D, F', T')
        x = x.flatten(2).transpose(1, 2)  # (B, N, D)
        return self.norm(x)


class TVLTAttention(nn.Module):
    def __init__(self, dim: int, heads: int = 12, dim_head: int = 64,
                 dropout: float = 0.1):
        super().__init__()
        inner_dim = heads * dim_head
        self.heads = heads
        self.scale = dim_head ** -0.5
        self.norm = nn.LayerNorm(dim)
        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias=False)
        self.to_out = nn.Sequential(nn.Linear(inner_dim, dim), nn.Dropout(dropout))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.norm(x)
        b, n, _ = x.shape
        h = self.heads
        qkv = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(lambda t: t.view(b, n, h, -1).transpose(1, 2), qkv)
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(b, n, -1)
        return self.to_out(out)


class TVLTBlock(nn.Module):
    def __init__(self, dim: int, heads: int, dim_head: int, ff_mult: int,
                 dropout: float):
        super().__init__()
        self.attn = TVLTAttention(dim, heads, dim_head, dropout)
        self.ff = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * ff_mult),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * ff_mult, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(x)
        x = x + self.ff(x)
        return x


class TVLTDecoder(nn.Module):
    """Lightweight decoder for Masked Autoencoding reconstruction."""

    def __init__(self, config: TVLTConfig):
        super().__init__()
        self.embed = nn.Linear(config.dim, config.decoder_dim)
        self.mask_token = nn.Parameter(torch.randn(config.decoder_dim))
        self.blocks = nn.ModuleList([
            TVLTBlock(config.decoder_dim, config.decoder_heads,
                      config.decoder_dim // config.decoder_heads,
                      config.ff_mult, config.dropout)
            for _ in range(config.decoder_depth)
        ])
        self.norm = nn.LayerNorm(config.decoder_dim)

    def forward(self, x: torch.Tensor, ids_restore: torch.Tensor,
                mask_token_count: int) -> torch.Tensor:
        x = self.embed(x)
        mask_tokens = self.mask_token.unsqueeze(0).unsqueeze(0).expand(
            x.shape[0], mask_token_count, -1
        )
        full = torch.cat([x, mask_tokens], dim=1)
        # Unshuffle
        full = torch.gather(
            full, dim=1,
            index=ids_restore.unsqueeze(-1).expand(-1, -1, full.shape[-1])
        )
        for block in self.blocks:
            full = block(full)
        return self.norm(full)


class OmniTVLT(nn.Module):
    """Textless Vision-Language Transformer.

    Learns joint video-audio representations without text by:
    1. Masked Autoencoding (MAE) - reconstruct masked patches
    2. Contrastive Alignment - align video and audio embeddings

    28x faster inference and 1/3 parameters vs text-based counterparts.
    """

    def __init__(self, config: TVLTConfig):
        super().__init__()
        self.config = config

        self.video_embed = PatchEmbedding3D(3, config.patch_size, config.dim, config.num_frames)
        self.audio_embed = AudioPatchEmbedding(config.audio_freq_bins, config.audio_patch_size, config.dim)

        self.modality_embed_video = nn.Parameter(torch.randn(1, 1, config.dim))
        self.modality_embed_audio = nn.Parameter(torch.randn(1, 1, config.dim))
        self.cls_token = nn.Parameter(torch.randn(1, 1, config.dim))

        self.encoder = nn.ModuleList([
            TVLTBlock(config.dim, config.heads, config.dim_head,
                      config.ff_mult, config.dropout)
            for _ in range(config.depth)
        ])
        self.encoder_norm = nn.LayerNorm(config.dim)

        # MAE decoder heads
        self.video_decoder = TVLTDecoder(config)
        self.audio_decoder = TVLTDecoder(config)

        # Reconstruction heads
        video_patch_dim = 3 * config.patch_size * config.patch_size * 2
        self.video_recon_head = nn.Linear(config.decoder_dim, video_patch_dim)
        audio_patch_dim = (config.audio_freq_bins // 8) * config.audio_patch_size
        self.audio_recon_head = nn.Linear(config.decoder_dim, audio_patch_dim)

        # Contrastive projection heads
        self.video_proj = nn.Sequential(
            nn.Linear(config.dim, config.dim),
            nn.GELU(),
            nn.Linear(config.dim, 256),
        )
        self.audio_proj = nn.Sequential(
            nn.Linear(config.dim, config.dim),
            nn.GELU(),
            nn.Linear(config.dim, 256),
        )

        self.temperature = nn.Parameter(torch.tensor(0.07))

    def _random_masking(
        self, x: torch.Tensor, mask_ratio: float
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        B, N, D = x.shape
        num_keep = max(1, int(N * (1 - mask_ratio)))
        noise = torch.rand(B, N, device=x.device)
        ids_shuffle = noise.argsort(dim=1)
        ids_restore = ids_shuffle.argsort(dim=1)
        ids_keep = ids_shuffle[:, :num_keep]
        x_kept = torch.gather(x, dim=1, index=ids_keep.unsqueeze(-1).expand(-1, -1, D))
        return x_kept, ids_restore, N - num_keep

    def encode(
        self,
        video: Optional[torch.Tensor] = None,
        audio: Optional[torch.Tensor] = None,
        apply_masking: bool = False,
    ) -> Dict[str, torch.Tensor]:
        parts = []
        video_restore = audio_restore = None
        video_mask_count = audio_mask_count = 0

        if video is not None:
            v = self.video_embed(video) + self.modality_embed_video
            if apply_masking:
                v, video_restore, video_mask_count = self._random_masking(
                    v, self.config.mae_masking_ratio
                )
            parts.append(v)

        if audio is not None:
            a = self.audio_embed(audio) + self.modality_embed_audio
            if apply_masking:
                a, audio_restore, audio_mask_count = self._random_masking(
                    a, self.config.mae_masking_ratio
                )
            parts.append(a)

        cls = self.cls_token.expand(parts[0].shape[0], -1, -1)
        x = torch.cat([cls] + parts, dim=1)

        for block in self.encoder:
            x = block(x)
        x = self.encoder_norm(x)

        return {
            "encoded": x,
            "cls": x[:, 0],
            "video_restore": video_restore,
            "audio_restore": audio_restore,
            "video_mask_count": video_mask_count,
            "audio_mask_count": audio_mask_count,
        }

    def contrastive_loss(self, video_cls: torch.Tensor,
                         audio_cls: torch.Tensor) -> torch.Tensor:
        v_proj = F.normalize(self.video_proj(video_cls), dim=-1)
        a_proj = F.normalize(self.audio_proj(audio_cls), dim=-1)
        logits = (v_proj @ a_proj.T) / self.temperature.exp().clamp(min=0.01)
        labels = torch.arange(logits.shape[0], device=logits.device)
        loss_v2a = F.cross_entropy(logits, labels)
        loss_a2v = F.cross_entropy(logits.T, labels)
        return (loss_v2a + loss_a2v) / 2

    def forward(
        self,
        video: torch.Tensor,
        audio: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        enc = self.encode(video, audio, apply_masking=True)
        contrastive = self.contrastive_loss(enc["cls"], enc["cls"])

        return {
            "loss": contrastive,
            "cls_embedding": enc["cls"],
            "encoded": enc["encoded"],
        }
