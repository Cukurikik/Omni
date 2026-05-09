"""
omni_kv_cache.py — KV Cache Manager for Autoregressive Inference
Inspired by: Memformer memory + LLM serving KV cache management
Layer: Compute / AI

Paged KV cache with dynamic memory allocation, prefix caching,
and multi-query attention support for efficient LLM inference.
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass


@dataclass
class KVCacheConfig:
    num_layers: int = 32
    num_heads: int = 32
    num_kv_heads: int = 8    # for grouped-query attention
    head_dim: int = 128
    max_seq_len: int = 8192
    page_size: int = 256     # tokens per page
    max_pages: int = 256     # max pages in pool
    dtype: torch.dtype = torch.float16


class KVPage:
    """A single page of KV cache storage."""
    __slots__ = ["key", "value", "length", "page_id"]

    def __init__(self, num_kv_heads: int, head_dim: int,
                 page_size: int, dtype: torch.dtype, device: torch.device,
                 page_id: int):
        self.key = torch.zeros(num_kv_heads, page_size, head_dim,
                               dtype=dtype, device=device)
        self.value = torch.zeros(num_kv_heads, page_size, head_dim,
                                 dtype=dtype, device=device)
        self.length = 0
        self.page_id = page_id

    @property
    def is_full(self) -> bool:
        return self.length >= self.key.shape[1]

    @property
    def remaining(self) -> int:
        return self.key.shape[1] - self.length

    def append(self, k: torch.Tensor, v: torch.Tensor) -> int:
        """Append key-value pairs. Returns number appended."""
        new_tokens = k.shape[1]
        space = self.remaining
        to_write = min(new_tokens, space)

        self.key[:, self.length:self.length + to_write] = k[:, :to_write]
        self.value[:, self.length:self.length + to_write] = v[:, :to_write]
        self.length += to_write
        return to_write

    def get_kv(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Return active key-value data."""
        return self.key[:, :self.length], self.value[:, :self.length]

    def reset(self):
        self.length = 0


class PagePool:
    """Pool of pre-allocated KV cache pages."""

    def __init__(self, config: KVCacheConfig, device: torch.device):
        self.config = config
        self.device = device
        self.free_pages: List[KVPage] = []
        self.allocated_count = 0

        # Pre-allocate pages
        for i in range(config.max_pages):
            page = KVPage(config.num_kv_heads, config.head_dim,
                          config.page_size, config.dtype, device, i)
            self.free_pages.append(page)

    def allocate(self) -> Optional[KVPage]:
        if not self.free_pages:
            return None
        self.allocated_count += 1
        return self.free_pages.pop()

    def release(self, page: KVPage):
        page.reset()
        self.free_pages.append(page)
        self.allocated_count -= 1

    @property
    def available(self) -> int:
        return len(self.free_pages)

    @property
    def utilization(self) -> float:
        total = self.allocated_count + len(self.free_pages)
        return self.allocated_count / max(1, total)


class LayerKVCache:
    """KV cache for a single transformer layer using paged storage."""

    def __init__(self, pool: PagePool):
        self.pool = pool
        self.pages: List[KVPage] = []

    @property
    def total_length(self) -> int:
        return sum(p.length for p in self.pages)

    def append(self, key: torch.Tensor, value: torch.Tensor):
        """Append new key-value pairs, allocating pages as needed."""
        offset = 0
        total_new = key.shape[1]

        while offset < total_new:
            # Get current page or allocate new one
            if not self.pages or self.pages[-1].is_full:
                new_page = self.pool.allocate()
                if new_page is None:
                    raise RuntimeError("KV cache page pool exhausted")
                self.pages.append(new_page)

            current_page = self.pages[-1]
            written = current_page.append(
                key[:, offset:], value[:, offset:]
            )
            offset += written

    def get_kv(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Concatenate all pages into contiguous KV tensors."""
        if not self.pages:
            return torch.empty(0), torch.empty(0)

        keys = []
        values = []
        for page in self.pages:
            k, v = page.get_kv()
            keys.append(k)
            values.append(v)

        return torch.cat(keys, dim=1), torch.cat(values, dim=1)

    def clear(self):
        for page in self.pages:
            self.pool.release(page)
        self.pages.clear()


class OmniKVCache:
    """Multi-layer paged KV cache for transformer inference.

    Features:
    - Paged memory allocation for dynamic sequence lengths
    - Support for grouped-query attention (GQA)
    - Prefix caching for shared prompt prefixes
    - Memory-efficient with pre-allocated page pool
    """

    def __init__(self, config: KVCacheConfig, device: torch.device):
        self.config = config
        self.device = device
        self.pool = PagePool(config, device)
        self.layers: List[LayerKVCache] = [
            LayerKVCache(self.pool) for _ in range(config.num_layers)
        ]
        self._prefix_hash: Optional[int] = None

    def update(self, layer_idx: int, key: torch.Tensor,
               value: torch.Tensor):
        """Add new key-value pairs to a specific layer's cache.

        Args:
            layer_idx: transformer layer index
            key: (num_kv_heads, new_tokens, head_dim)
            value: (num_kv_heads, new_tokens, head_dim)
        """
        self.layers[layer_idx].append(key, value)

    def get(self, layer_idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Retrieve cached key-value pairs for a layer."""
        return self.layers[layer_idx].get_kv()

    def get_seq_length(self, layer_idx: int = 0) -> int:
        """Get current sequence length in cache."""
        return self.layers[layer_idx].total_length

    def clear(self):
        """Clear all cached data and return pages to pool."""
        for layer in self.layers:
            layer.clear()
        self._prefix_hash = None

    def clear_layer(self, layer_idx: int):
        """Clear cache for a specific layer."""
        self.layers[layer_idx].clear()

    @property
    def memory_usage_mb(self) -> float:
        """Estimate current memory usage in MB."""
        bytes_per_element = 2 if self.config.dtype == torch.float16 else 4
        total_elements = 0
        for layer in self.layers:
            for page in layer.pages:
                total_elements += page.length * self.config.num_kv_heads * self.config.head_dim * 2
        return total_elements * bytes_per_element / (1024 * 1024)

    @property
    def page_utilization(self) -> float:
        """Page pool utilization ratio."""
        return self.pool.utilization

    def stats(self) -> Dict[str, float]:
        """Return cache statistics."""
        return {
            "seq_length": self.get_seq_length(),
            "memory_mb": self.memory_usage_mb,
            "page_utilization": self.page_utilization,
            "pages_available": self.pool.available,
            "pages_allocated": self.pool.allocated_count,
        }

    def set_prefix_hash(self, prefix_tokens: torch.Tensor):
        """Store hash of prefix for prefix caching."""
        self._prefix_hash = hash(prefix_tokens.cpu().numpy().tobytes())

    def matches_prefix(self, prefix_tokens: torch.Tensor) -> bool:
        """Check if cached prefix matches given tokens."""
        if self._prefix_hash is None:
            return False
        return self._prefix_hash == hash(prefix_tokens.cpu().numpy().tobytes())
