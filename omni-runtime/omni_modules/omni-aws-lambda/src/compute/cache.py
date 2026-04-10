"""omni-aws-lambda â€” Compute Cache Layer"""
from typing import Any, Optional
from collections import OrderedDict
import time

class ComputeCache:
    def __init__(self, max_size: int = 1000, ttl_ms: int = 60000):
        self.max_size = max_size; self.ttl_ms = ttl_ms; self._store: OrderedDict = OrderedDict(); self.hits = 0; self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            val, ts = self._store[key]
            if (time.time() * 1000 - ts) < self.ttl_ms: self.hits += 1; self._store.move_to_end(key); return val
            else: del self._store[key]
        self.misses += 1; return None

    def set(self, key: str, value: Any):
        if key in self._store: self._store.move_to_end(key)
        self._store[key] = (value, time.time() * 1000)
        while len(self._store) > self.max_size: self._store.popitem(last=False)

    def invalidate(self, key: str): self._store.pop(key, None)
    def clear(self): self._store.clear()
    def size(self) -> int: return len(self._store)
    def hit_rate(self) -> float: total = self.hits + self.misses; return self.hits / total if total > 0 else 0.0