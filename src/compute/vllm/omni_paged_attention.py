"""
@omni-layer Compute | @omni-source vllm-project/vllm
@omni-description PagedAttention KV-cache manager: block-based virtual memory
for efficient KV-cache management during batched inference.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class KVBlock:
    __slots__ = ("block_id","tokens","k_cache","v_cache","ref_count")
    def __init__(self, block_id, block_size, d):
        self.block_id = block_id; self.tokens = 0
        self.k_cache = [[0.0]*d for _ in range(block_size)]
        self.v_cache = [[0.0]*d for _ in range(block_size)]
        self.ref_count = 1

class OmniPagedAttention:
    def __init__(self, block_size=16, d=128, n_blocks=1024):
        self.block_size = block_size; self.d = d; self.n_blocks = n_blocks
        self.free_blocks: List[int] = list(range(n_blocks))
        self.blocks: Dict[int, KVBlock] = {}

    def allocate_block(self) -> OmniResult:
        try:
            if not self.free_blocks: return OmniResult(error=Exception("OOM: no free blocks"))
            bid = self.free_blocks.pop(0)
            block = KVBlock(bid, self.block_size, self.d)
            self.blocks[bid] = block
            return OmniResult(data={"block_id": bid, "free_remaining": len(self.free_blocks)})
        except Exception as e: return OmniResult(error=e)

    def write_kv(self, block_id: int, k: List[float], v: List[float]) -> OmniResult:
        try:
            if block_id not in self.blocks: return OmniResult(error=Exception("Invalid block"))
            block = self.blocks[block_id]
            if block.tokens >= self.block_size: return OmniResult(error=Exception("Block full"))
            pos = block.tokens
            block.k_cache[pos] = k[:self.d]; block.v_cache[pos] = v[:self.d]
            block.tokens += 1
            return OmniResult(data={"block_id": block_id, "slot": pos, "fill": block.tokens/self.block_size})
        except Exception as e: return OmniResult(error=e)

    def free_block(self, block_id: int) -> OmniResult:
        try:
            if block_id not in self.blocks: return OmniResult(error=Exception("Invalid block"))
            del self.blocks[block_id]
            self.free_blocks.append(block_id)
            return OmniResult(data={"freed": block_id, "free_total": len(self.free_blocks)})
        except Exception as e: return OmniResult(error=e)

    def utilization(self) -> OmniResult:
        used = len(self.blocks); total_slots = sum(b.tokens for b in self.blocks.values())
        return OmniResult(data={"blocks_used": used, "blocks_free": len(self.free_blocks), "slots_used": total_slots, "utilization": used/max(self.n_blocks,1), "memory_mb": used*self.block_size*self.d*4*2/(1024*1024)})
