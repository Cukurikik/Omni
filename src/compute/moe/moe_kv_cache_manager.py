"""
moe_kv_cache_manager.py — Expert-Aware KV Cache for MoE Models
Reference: vLLM paged attention, MoE cache strategies
Layer: Compute / AI — MoE Inference Memory

Manages separate KV caches per expert, with shared-expert cache pooling,
cache eviction based on expert routing predictions, and memory-efficient
paging for long-context MoE inference.
"""
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class KVCacheConfig:
    num_experts: int = 8
    num_layers: int = 12
    num_heads: int = 12
    head_dim: int = 64
    max_seq_len: int = 4096
    block_size: int = 16
    max_blocks_per_expert: int = 256
    dtype: torch.dtype = torch.float16


class KVBlock:
    """Single block of KV cache for paged attention."""
    __slots__ = ['key', 'value', 'num_tokens', 'block_id']

    def __init__(self, num_heads, head_dim, block_size, dtype, device):
        self.key = torch.zeros(block_size, num_heads, head_dim, dtype=dtype, device=device)
        self.value = torch.zeros(block_size, num_heads, head_dim, dtype=dtype, device=device)
        self.num_tokens = 0
        self.block_id = -1

    @property
    def is_full(self):
        return self.num_tokens >= self.key.shape[0]

    @property
    def remaining(self):
        return self.key.shape[0] - self.num_tokens

    def append(self, k, v):
        """Append key-value pairs to this block."""
        n = min(k.shape[0], self.remaining)
        if n <= 0:
            return 0
        self.key[self.num_tokens:self.num_tokens + n] = k[:n]
        self.value[self.num_tokens:self.num_tokens + n] = v[:n]
        self.num_tokens += n
        return n

    def clear(self):
        self.key.zero_()
        self.value.zero_()
        self.num_tokens = 0


class BlockPool:
    """Pool of reusable KV blocks to avoid repeated allocation."""
    def __init__(self, max_blocks, num_heads, head_dim, block_size, dtype, device):
        self.pool = []
        self.free_ids = list(range(max_blocks))
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.block_size = block_size
        self.dtype = dtype
        self.device = device
        # Pre-allocate all blocks
        for i in range(max_blocks):
            blk = KVBlock(num_heads, head_dim, block_size, dtype, device)
            blk.block_id = i
            self.pool.append(blk)

    def allocate(self) -> Optional[KVBlock]:
        if not self.free_ids:
            return None
        bid = self.free_ids.pop()
        return self.pool[bid]

    def release(self, block: KVBlock):
        block.clear()
        self.free_ids.append(block.block_id)

    @property
    def num_free(self):
        return len(self.free_ids)

    @property
    def num_used(self):
        return len(self.pool) - len(self.free_ids)


class ExpertKVCache:
    """Per-expert KV cache using paged blocks."""
    def __init__(self, expert_id, pool: BlockPool):
        self.expert_id = expert_id
        self.pool = pool
        self.blocks: List[KVBlock] = []
        self.total_tokens = 0

    def append(self, k: torch.Tensor, v: torch.Tensor) -> int:
        """Append KV pairs, allocating new blocks as needed."""
        remaining = k.shape[0]
        offset = 0
        while remaining > 0:
            if not self.blocks or self.blocks[-1].is_full:
                new_block = self.pool.allocate()
                if new_block is None:
                    break  # Out of memory
                self.blocks.append(new_block)
            added = self.blocks[-1].append(k[offset:], v[offset:])
            offset += added
            remaining -= added
            self.total_tokens += added
        return offset

    def get_kv(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get concatenated KV cache."""
        if not self.blocks:
            return torch.empty(0), torch.empty(0)
        keys = [b.key[:b.num_tokens] for b in self.blocks]
        vals = [b.value[:b.num_tokens] for b in self.blocks]
        return torch.cat(keys, dim=0), torch.cat(vals, dim=0)

    def clear(self):
        for block in self.blocks:
            self.pool.release(block)
        self.blocks.clear()
        self.total_tokens = 0

    @property
    def num_blocks(self):
        return len(self.blocks)


class MoEKVCacheManager:
    """Manages KV caches across all experts in all layers."""
    def __init__(self, config: KVCacheConfig, device: torch.device = None):
        self.config = config
        self.device = device or torch.device("cpu")

        total_blocks = config.max_blocks_per_expert * config.num_experts
        self.pool = BlockPool(
            total_blocks, config.num_heads, config.head_dim,
            config.block_size, config.dtype, self.device)

        # caches[layer][expert_id] = ExpertKVCache
        self.caches: Dict[int, Dict[int, ExpertKVCache]] = {}
        for layer in range(config.num_layers):
            self.caches[layer] = {}
            for e in range(config.num_experts):
                self.caches[layer][e] = ExpertKVCache(e, self.pool)

    def append(self, layer: int, expert_id: int,
               k: torch.Tensor, v: torch.Tensor) -> int:
        """Append KV for a specific layer and expert."""
        return self.caches[layer][expert_id].append(k, v)

    def get_kv(self, layer: int, expert_id: int):
        """Get cached KV for a specific layer and expert."""
        return self.caches[layer][expert_id].get_kv()

    def clear_expert(self, layer: int, expert_id: int):
        self.caches[layer][expert_id].clear()

    def clear_all(self):
        for layer in self.caches:
            for e in self.caches[layer]:
                self.caches[layer][e].clear()

    def memory_usage_mb(self):
        used = self.pool.num_used
        bytes_per_block = (
            self.config.block_size * self.config.num_heads *
            self.config.head_dim * 2 *  # K + V
            (2 if self.config.dtype == torch.float16 else 4))
        return used * bytes_per_block / (1024 * 1024)

    def utilization_report(self):
        report = {"total_blocks": len(self.pool.pool),
                  "used_blocks": self.pool.num_used,
                  "free_blocks": self.pool.num_free,
                  "memory_mb": self.memory_usage_mb(),
                  "per_layer": {}}
        for layer in self.caches:
            layer_info = {}
            for e, cache in self.caches[layer].items():
                layer_info[e] = {"tokens": cache.total_tokens,
                                 "blocks": cache.num_blocks}
            report["per_layer"][layer] = layer_info
        return report
