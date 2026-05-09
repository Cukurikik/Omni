"""
@omni-layer Compute | @omni-source huggingface/transformers (attention_sinks)
@omni-description Attention sink manager: KV-cache management for infinite-length
generation by preserving initial attention sink tokens.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniAttentionSinkManager:
    def __init__(self, window_size=1024, sink_size=4, d=256, n_heads=8):
        self.window_size = window_size; self.sink_size = sink_size
        self.d = d; self.n_heads = n_heads
        self.k_cache: List[List[float]] = []; self.v_cache: List[List[float]] = []

    def append_to_cache(self, k: List[float], v: List[float]) -> OmniResult:
        try:
            self.k_cache.append(k); self.v_cache.append(v)
            if len(self.k_cache) > self.window_size + self.sink_size:
                self._evict()
            return OmniResult(data={"cache_len": len(self.k_cache), "window": self.window_size, "sinks": self.sink_size})
        except Exception as e: return OmniResult(error=e)

    def _evict(self):
        total = len(self.k_cache)
        if total <= self.window_size + self.sink_size: return
        keep_start = self.k_cache[:self.sink_size]
        keep_end = self.k_cache[-(self.window_size):]
        self.k_cache = keep_start + keep_end
        keep_v_start = self.v_cache[:self.sink_size]
        keep_v_end = self.v_cache[-(self.window_size):]
        self.v_cache = keep_v_start + keep_v_end

    def get_effective_cache(self) -> OmniResult:
        try:
            return OmniResult(data={"keys": self.k_cache, "values": self.v_cache, "effective_len": len(self.k_cache), "sink_tokens": self.sink_size, "window_tokens": min(len(self.k_cache)-self.sink_size, self.window_size)})
        except Exception as e: return OmniResult(error=e)

    def cache_stats(self) -> OmniResult:
        total = len(self.k_cache)
        mem_bytes = total * self.d * 4 * 2
        return OmniResult(data={"total_cached": total, "memory_mb": mem_bytes/(1024*1024), "utilization": total/(self.window_size+self.sink_size)})
