"""
OMNI Transformer — KV Cache Manager
Production KV-cache management with paged attention support.
Learned from: vLLM PagedAttention, inference optimization patterns
"""
import torch
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class KVCacheConfig:
    num_layers: int = 32
    num_kv_heads: int = 8
    head_dim: int = 128
    max_seq_len: int = 8192
    page_size: int = 16  # Tokens per page
    max_pages: int = 1024
    dtype: torch.dtype = torch.float16


class KVCacheBlock:
    """Single KV cache block for one layer."""
    def __init__(self, max_seq_len: int, num_heads: int, head_dim: int, dtype: torch.dtype, device: torch.device):
        self.key_cache = torch.zeros(1, num_heads, max_seq_len, head_dim, dtype=dtype, device=device)
        self.value_cache = torch.zeros(1, num_heads, max_seq_len, head_dim, dtype=dtype, device=device)
        self.seq_len = 0

    def append(self, key: torch.Tensor, value: torch.Tensor) -> None:
        new_tokens = key.size(2)
        end = self.seq_len + new_tokens
        self.key_cache[:, :, self.seq_len:end, :] = key
        self.value_cache[:, :, self.seq_len:end, :] = value
        self.seq_len = end

    def get(self) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.key_cache[:, :, :self.seq_len, :], self.value_cache[:, :, :self.seq_len, :]

    def clear(self) -> None:
        self.key_cache.zero_()
        self.value_cache.zero_()
        self.seq_len = 0


class PagedKVCache:
    """Paged KV cache inspired by vLLM for efficient memory utilization."""
    def __init__(self, config: KVCacheConfig, device: torch.device):
        self.config = config
        self.device = device
        self.page_pool: List[torch.Tensor] = []
        self.allocated_pages: Dict[int, List[int]] = {}  # sequence_id -> list of page indices
        self._init_pool()

    def _init_pool(self) -> None:
        for _ in range(self.config.max_pages):
            k_page = torch.zeros(self.config.num_kv_heads, self.config.page_size, self.config.head_dim,
                                 dtype=self.config.dtype, device=self.device)
            v_page = torch.zeros_like(k_page)
            self.page_pool.append((k_page, v_page))
        self.free_pages = list(range(self.config.max_pages))
        logger.info(f"Initialized PagedKVCache: {self.config.max_pages} pages, {self.config.page_size} tokens/page")

    def allocate_sequence(self, seq_id: int, num_tokens: int) -> bool:
        pages_needed = (num_tokens + self.config.page_size - 1) // self.config.page_size
        if len(self.free_pages) < pages_needed:
            logger.warning(f"Not enough pages for sequence {seq_id}: need {pages_needed}, have {len(self.free_pages)}")
            return False
        pages = [self.free_pages.pop() for _ in range(pages_needed)]
        self.allocated_pages[seq_id] = pages
        return True

    def free_sequence(self, seq_id: int) -> None:
        if seq_id in self.allocated_pages:
            pages = self.allocated_pages.pop(seq_id)
            self.free_pages.extend(pages)

    def get_cache(self, seq_id: int) -> Optional[Tuple[torch.Tensor, torch.Tensor]]:
        if seq_id not in self.allocated_pages:
            return None
        pages = self.allocated_pages[seq_id]
        k_pages = [self.page_pool[p][0] for p in pages]
        v_pages = [self.page_pool[p][1] for p in pages]
        return torch.cat(k_pages, dim=1), torch.cat(v_pages, dim=1)

    @property
    def utilization(self) -> float:
        used = self.config.max_pages - len(self.free_pages)
        return used / self.config.max_pages if self.config.max_pages > 0 else 0.0


class KVCacheManager:
    """Manages KV caches across all layers for inference."""
    def __init__(self, config: KVCacheConfig, device: Optional[torch.device] = None):
        self.config = config
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.caches: List[KVCacheBlock] = [
            KVCacheBlock(config.max_seq_len, config.num_kv_heads, config.head_dim, config.dtype, self.device)
            for _ in range(config.num_layers)
        ]

    def get_layer_cache(self, layer_idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.caches[layer_idx].get()

    def update_layer_cache(self, layer_idx: int, key: torch.Tensor, value: torch.Tensor) -> None:
        self.caches[layer_idx].append(key, value)

    def clear(self) -> None:
        for cache in self.caches:
            cache.clear()

    @property
    def memory_usage_mb(self) -> float:
        total = sum(c.key_cache.numel() + c.value_cache.numel() for c in self.caches)
        return total * 2 / (1024 * 1024)  # Assuming fp16
