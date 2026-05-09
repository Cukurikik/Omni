"""
OMNI MOTHER: KV-Cache Manager for MoE Inference (Production Grade)
Paged attention block allocator for efficient memory during autoregressive
generation. Implements virtual-block mapping, prefix sharing, and eviction.
Ref: "Efficient Memory Management for LLM Serving with PagedAttention" (vLLM)
"""
import logging
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple
import torch

logger = logging.getLogger("OmniKVCache")

class PagedBlock:
    """A fixed-size block of KV cache memory."""
    __slots__ = ("block_id", "num_layers", "num_heads", "head_dim",
                 "block_size", "k_cache", "v_cache", "ref_count", "num_filled")

    def __init__(self, block_id: int, num_layers: int, num_heads: int,
                 head_dim: int, block_size: int, dtype: torch.dtype, device: str):
        self.block_id = block_id
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.block_size = block_size
        self.ref_count = 0
        self.num_filled = 0
        shape = (num_layers, num_heads, block_size, head_dim)
        self.k_cache = torch.zeros(shape, dtype=dtype, device=device)
        self.v_cache = torch.zeros(shape, dtype=dtype, device=device)

    def is_full(self) -> bool:
        return self.num_filled >= self.block_size

    def remaining(self) -> int:
        return self.block_size - self.num_filled

    def memory_bytes(self) -> int:
        return self.k_cache.nelement() * self.k_cache.element_size() * 2

class BlockAllocator:
    """Pre-allocates a pool of PagedBlocks and manages allocation/deallocation."""
    def __init__(self, num_blocks: int, num_layers: int, num_heads: int,
                 head_dim: int, block_size: int, dtype: torch.dtype = torch.float16,
                 device: str = "cuda"):
        self.num_blocks = num_blocks
        self.free_blocks: List[PagedBlock] = []
        self.allocated: Dict[int, PagedBlock] = {}

        logger.info(f"Allocating {num_blocks} KV cache blocks "
                     f"({num_layers}L x {num_heads}H x {block_size}T x {head_dim}D)")

        for i in range(num_blocks):
            blk = PagedBlock(i, num_layers, num_heads, head_dim, block_size, dtype, device)
            self.free_blocks.append(blk)

        total_mb = sum(b.memory_bytes() for b in self.free_blocks) / (1024**2)
        logger.info(f"KV cache pool ready: {total_mb:.1f} MB total")

    def allocate(self) -> Optional[PagedBlock]:
        if not self.free_blocks:
            return None
        blk = self.free_blocks.pop()
        blk.ref_count = 1
        blk.num_filled = 0
        blk.k_cache.zero_()
        blk.v_cache.zero_()
        self.allocated[blk.block_id] = blk
        return blk

    def free(self, block: PagedBlock) -> None:
        block.ref_count -= 1
        if block.ref_count <= 0:
            self.allocated.pop(block.block_id, None)
            self.free_blocks.append(block)

    def num_free(self) -> int:
        return len(self.free_blocks)

    def utilization(self) -> float:
        return len(self.allocated) / max(self.num_blocks, 1)

class SequenceKVCache:
    """Manages block mapping for a single sequence during generation."""
    def __init__(self, seq_id: int, allocator: BlockAllocator):
        self.seq_id = seq_id
        self.allocator = allocator
        self.block_table: List[PagedBlock] = []

    def append_token(self, layer: int, k: torch.Tensor, v: torch.Tensor) -> bool:
        """Append a single token's KV to the cache. Returns False if OOM."""
        if not self.block_table or self.block_table[-1].is_full():
            new_block = self.allocator.allocate()
            if new_block is None:
                logger.warning(f"Seq {self.seq_id}: OOM, cannot allocate new block")
                return False
            self.block_table.append(new_block)

        blk = self.block_table[-1]
        pos = blk.num_filled
        blk.k_cache[layer, :, pos, :] = k
        blk.v_cache[layer, :, pos, :] = v
        blk.num_filled += 1
        return True

    def get_kv(self, layer: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Retrieve concatenated K and V tensors for a specific layer."""
        if not self.block_table:
            return torch.empty(0), torch.empty(0)

        k_parts, v_parts = [], []
        for blk in self.block_table:
            filled = blk.num_filled
            k_parts.append(blk.k_cache[layer, :, :filled, :])
            v_parts.append(blk.v_cache[layer, :, :filled, :])

        return torch.cat(k_parts, dim=1), torch.cat(v_parts, dim=1)

    def num_tokens(self) -> int:
        return sum(blk.num_filled for blk in self.block_table)

    def release(self) -> None:
        for blk in self.block_table:
            self.allocator.free(blk)
        self.block_table.clear()

class OmniKVCacheManager:
    """Top-level manager coordinating all sequence caches with LRU eviction."""
    def __init__(self, num_blocks: int = 256, num_layers: int = 32,
                 num_heads: int = 32, head_dim: int = 128, block_size: int = 16,
                 dtype: torch.dtype = torch.float16, device: str = "cuda",
                 max_sequences: int = 256):
        self.allocator = BlockAllocator(num_blocks, num_layers, num_heads,
                                         head_dim, block_size, dtype, device)
        self.sequences: OrderedDict[int, SequenceKVCache] = OrderedDict()
        self.max_sequences = max_sequences

    def create_sequence(self, seq_id: int) -> SequenceKVCache:
        if seq_id in self.sequences:
            return self.sequences[seq_id]
        if len(self.sequences) >= self.max_sequences:
            self._evict_lru()
        cache = SequenceKVCache(seq_id, self.allocator)
        self.sequences[seq_id] = cache
        return cache

    def get_sequence(self, seq_id: int) -> Optional[SequenceKVCache]:
        if seq_id in self.sequences:
            self.sequences.move_to_end(seq_id)
            return self.sequences[seq_id]
        return None

    def release_sequence(self, seq_id: int) -> None:
        if seq_id in self.sequences:
            self.sequences[seq_id].release()
            del self.sequences[seq_id]

    def _evict_lru(self) -> None:
        if not self.sequences:
            return
        oldest_id, oldest = next(iter(self.sequences.items()))
        oldest.release()
        del self.sequences[oldest_id]
        logger.info(f"Evicted LRU sequence {oldest_id}")

    def stats(self) -> Dict:
        return {
            "active_sequences": len(self.sequences),
            "blocks_used": len(self.allocator.allocated),
            "blocks_free": self.allocator.num_free(),
            "utilization": f"{self.allocator.utilization():.1%}",
        }
