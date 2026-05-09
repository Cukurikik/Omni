"""OMNI Compute — Attention Sink / StreamingLLM Engine"""
import logging; from typing import List, Dict
logger = logging.getLogger("omni.attn_sink")

class AttentionSinkManager:
    """StreamingLLM: keep initial sink tokens + rolling window for infinite context."""
    def __init__(self, sink_tokens: int = 4, window_size: int = 1024):
        self.sink_tokens = sink_tokens; self.window_size = window_size
        self.kv_cache: List[Dict] = []
        self.total_tokens_seen = 0
    def should_evict(self) -> bool:
        return len(self.kv_cache) > self.sink_tokens + self.window_size
    def evict(self):
        if not self.should_evict(): return
        keep = self.sink_tokens + self.window_size
        sink_part = self.kv_cache[:self.sink_tokens]
        window_part = self.kv_cache[-(self.window_size):]
        evicted = len(self.kv_cache) - keep
        self.kv_cache = sink_part + window_part
        logger.debug(f"Evicted {evicted} KV entries, kept {len(self.kv_cache)}")
    def add_token(self, kv_entry: Dict):
        self.kv_cache.append(kv_entry); self.total_tokens_seen += 1
        if self.should_evict(): self.evict()
    def get_effective_context(self) -> List[Dict]: return self.kv_cache
    def stats(self) -> Dict:
        return {"cache_size": len(self.kv_cache), "sink_tokens": self.sink_tokens,
                "window_size": self.window_size, "total_seen": self.total_tokens_seen,
                "capacity": f"{len(self.kv_cache)}/{self.sink_tokens + self.window_size}"}
