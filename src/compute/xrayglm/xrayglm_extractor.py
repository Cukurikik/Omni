# XrayGLM — Medical Image Feature Extractor
import torch
from typing import Optional, Generic, TypeVar
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class XrayFeatureExtractor:
    MAX_RES = 2048; CHANNELS = [1, 3]
    def extract(self, image: torch.Tensor) -> OmniResult[torch.Tensor, str]:
        if image.dim() != 3: return OmniResult(error="Expected [C,H,W] tensor")
        c, h, w = image.shape
        if c not in self.CHANNELS: return OmniResult(error=f"Channels must be 1 or 3, got {c}")
        if h > self.MAX_RES or w > self.MAX_RES: return OmniResult(error=f"Resolution exceeds {self.MAX_RES}")
        # Production: ResNet/ViT forward pass -> pooled features
        pooled = image.mean(dim=[1, 2])  # [C] global average pool
        return OmniResult(value=pooled)
