"""OmniLruCacheEvictionEngine — Production-grade LRU cache with O(1) operations.

Implements Least Recently Used cache using OrderedDict for O(1) get/put/evict.
Tracks hit/miss statistics and supports capacity resizing.
"""
from collections import OrderedDict
from typing import Any, Dict, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniLruCacheEvictionEngine:
    """Production engine for LRU cache eviction policy."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("capacity must be positive.")
        self.capacity = capacity
        self._cache: OrderedDict = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Result:
        """Get value from cache. Moves key to most-recently-used position."""
        try:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._hits += 1
                return Ok({"key": key, "value": self._cache[key], "hit": True})
            self._misses += 1
            return Ok({"key": key, "value": None, "hit": False})
        except Exception as e:
            return Err(e)

    def put(self, key: str, value: Any) -> Result:
        """Insert or update key. Evicts LRU entry if at capacity."""
        try:
            evicted = None
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self.capacity:
                evicted_key, evicted_val = self._cache.popitem(last=False)
                evicted = {"key": evicted_key, "value": evicted_val}
            return Ok({"key": key, "stored": True, "evicted": evicted, "size": len(self._cache)})
        except Exception as e:
            return Err(e)

    def get_stats(self) -> Result:
        """Return cache hit/miss statistics."""
        total = self._hits + self._misses
        return Ok({"hits": self._hits, "misses": self._misses, "total_requests": total,
                    "hit_rate": round(self._hits / total, 6) if total > 0 else 0.0,
                    "size": len(self._cache), "capacity": self.capacity})

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniLruCacheEvictionEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "capacity": self.capacity, "complexity": "O(1) get/put via OrderedDict"}
