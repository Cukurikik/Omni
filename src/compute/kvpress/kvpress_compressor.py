# kvpress KV Cache Compression Pipeline
import torch
from typing import Optional, Generic, TypeVar, List
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class KVPress:
    MAX_SEQ = 131072; MAX_HEADS = 128; MAX_HEAD_DIM = 256
    def __init__(self, compression_ratio: float = 0.5):
        if compression_ratio <= 0 or compression_ratio > 1: raise ValueError("Ratio must be in (0,1]")
        self.compression_ratio = compression_ratio

    def compress_knorm(self, keys: torch.Tensor) -> OmniResult[torch.Tensor, str]:
        if keys.dim() != 4: return OmniResult(error="Expected [B, H, S, D] key tensor")
        b, h, s, d = keys.shape
        if s > self.MAX_SEQ: return OmniResult(error=f"Seq {s} exceeds {self.MAX_SEQ}")
        if h > self.MAX_HEADS: return OmniResult(error=f"Heads {h} exceeds {self.MAX_HEADS}")
        norms = keys.norm(dim=-1)  # [B, H, S]
        keep_count = max(1, int(s * self.compression_ratio))
        _, indices = norms.topk(keep_count, dim=-1, largest=True)
        indices_sorted, _ = indices.sort(dim=-1)
        compressed = keys.gather(2, indices_sorted.unsqueeze(-1).expand(-1, -1, -1, d))
        return OmniResult(value=compressed)

    def compress_expected_attention(self, keys: torch.Tensor, attn_weights: torch.Tensor) -> OmniResult[torch.Tensor, str]:
        if keys.dim() != 4: return OmniResult(error="Expected 4D key tensor")
        b, h, s, d = keys.shape
        if attn_weights.shape[-1] != s: return OmniResult(error="Attention shape mismatch")
        importance = attn_weights.mean(dim=-2)  # [B, H, S]
        keep_count = max(1, int(s * self.compression_ratio))
        _, indices = importance.topk(keep_count, dim=-1)
        indices_sorted, _ = indices.sort(dim=-1)
        compressed = keys.gather(2, indices_sorted.unsqueeze(-1).expand(-1, -1, -1, d))
        return OmniResult(value=compressed)
