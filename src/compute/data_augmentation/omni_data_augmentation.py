"""
omni_data_augmentation.py — Audio/Vision Augmentation Pipeline
Inspired by: SoundStorm/TVLT pretraining augmentations
Layer: Compute / Data
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class AugConfig:
    freq_mask_max: int = 27
    time_mask_max: int = 100
    num_freq_masks: int = 2
    num_time_masks: int = 2
    mixup_alpha: float = 0.4
    cutmix_alpha: float = 1.0
    random_crop_scale: Tuple[float, float] = (0.08, 1.0)
    color_jitter_strength: float = 0.5


class SpecAugment(nn.Module):
    """SpecAugment for audio spectrograms."""

    def __init__(self, config: AugConfig):
        super().__init__()
        self.config = config

    def forward(self, spec: torch.Tensor) -> torch.Tensor:
        if not self.training:
            return spec
        spec = spec.clone()
        _, freq, time = spec.shape

        for _ in range(self.config.num_freq_masks):
            f = torch.randint(0, min(self.config.freq_mask_max, freq), (1,)).item()
            f0 = torch.randint(0, max(1, freq - f), (1,)).item()
            spec[:, f0:f0 + f, :] = 0.0

        for _ in range(self.config.num_time_masks):
            t = torch.randint(0, min(self.config.time_mask_max, time), (1,)).item()
            t0 = torch.randint(0, max(1, time - t), (1,)).item()
            spec[:, :, t0:t0 + t] = 0.0

        return spec


class Mixup(nn.Module):
    """Mixup augmentation for contrastive learning."""

    def __init__(self, alpha: float = 0.4):
        super().__init__()
        self.alpha = alpha

    def forward(self, x: torch.Tensor, y: torch.Tensor
                ) -> Tuple[torch.Tensor, torch.Tensor, float]:
        if not self.training:
            return x, y, 1.0

        lam = torch.distributions.Beta(self.alpha, self.alpha).sample().item()
        lam = max(lam, 1.0 - lam)

        batch_size = x.shape[0]
        perm = torch.randperm(batch_size, device=x.device)

        mixed_x = lam * x + (1 - lam) * x[perm]
        mixed_y = lam * y + (1 - lam) * y[perm]

        return mixed_x, mixed_y, lam


class RandomResizedCrop(nn.Module):
    """Differentiable random resized crop for vision."""

    def __init__(self, size: int = 224, scale: Tuple[float, float] = (0.08, 1.0)):
        super().__init__()
        self.size = size
        self.scale = scale

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training:
            return F.interpolate(x, size=self.size, mode="bilinear", align_corners=False)

        B, C, H, W = x.shape
        area = H * W
        target_area = torch.empty(1).uniform_(self.scale[0], self.scale[1]).item() * area
        aspect_ratio = math.exp(torch.empty(1).uniform_(math.log(3/4), math.log(4/3)).item())

        w = int(round(math.sqrt(target_area * aspect_ratio)))
        h = int(round(math.sqrt(target_area / aspect_ratio)))
        w, h = min(w, W), min(h, H)

        i = torch.randint(0, max(1, H - h), (1,)).item()
        j = torch.randint(0, max(1, W - w), (1,)).item()

        cropped = x[:, :, i:i+h, j:j+w]
        return F.interpolate(cropped, size=self.size, mode="bilinear", align_corners=False)


class ColorJitter(nn.Module):
    """Simple differentiable color jitter for images."""

    def __init__(self, strength: float = 0.5):
        super().__init__()
        self.strength = strength

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training:
            return x

        # Brightness
        b_factor = 1.0 + (torch.rand(1, device=x.device).item() - 0.5) * 2 * self.strength * 0.4
        x = x * b_factor

        # Contrast
        c_factor = 1.0 + (torch.rand(1, device=x.device).item() - 0.5) * 2 * self.strength * 0.4
        mean = x.mean(dim=(-2, -1), keepdim=True)
        x = (x - mean) * c_factor + mean

        # Saturation (approximate)
        s_factor = 1.0 + (torch.rand(1, device=x.device).item() - 0.5) * 2 * self.strength * 0.4
        gray = x.mean(dim=-3, keepdim=True)
        x = (1 - s_factor) * gray + s_factor * x

        return x.clamp(0, 1)


class OmniAugmentationPipeline(nn.Module):
    """Combined augmentation pipeline for multimodal training."""

    def __init__(self, config: AugConfig = AugConfig()):
        super().__init__()
        self.spec_augment = SpecAugment(config)
        self.mixup = Mixup(config.mixup_alpha)
        self.random_crop = RandomResizedCrop(224, config.random_crop_scale)
        self.color_jitter = ColorJitter(config.color_jitter_strength)

    def augment_audio(self, spec: torch.Tensor) -> torch.Tensor:
        return self.spec_augment(spec)

    def augment_image(self, img: torch.Tensor) -> torch.Tensor:
        img = self.random_crop(img)
        img = self.color_jitter(img)
        return img

    def augment_pair(self, img: torch.Tensor, audio: torch.Tensor
                     ) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.augment_image(img), self.augment_audio(audio)
