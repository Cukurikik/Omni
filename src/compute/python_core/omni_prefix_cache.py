"""OMNI Compute — Prefix Caching Engine for prompt reuse."""
import hashlib, time, logging; from collections import OrderedDict
from dataclasses import dataclass; from typing import Dict, List, Optional, Tuple
logger = logging.getLogger("omni.prefix_cache")

class PrefixCache:
    """Cache computed KV-states for common prompt prefixes."""
    def __init__(self, max_entries: int = 1000, max_tokens: int = 100000):
        self.max_entries = max_entries; self.max_tokens = max_tokens
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.total_tokens = 0; self.hits = 0; self.misses = 0
    def _key(self, tokens: List[int]) -> str:
        return hashlib.md5(str(tokens).encode()).hexdigest()
    def get(self, prefix_tokens: List[int]) -> Optional[Dict]:
        key = self._key(prefix_tokens)
        if key in self.cache:
            self.cache.move_to_end(key); self.hits += 1
            return self.cache[key]
        self.misses += 1; return None
    def put(self, prefix_tokens: List[int], kv_state: Dict):
        key = self._key(prefix_tokens); n = len(prefix_tokens)
        while self.total_tokens + n > self.max_tokens and self.cache:
            _, old = self.cache.popitem(last=False)
            self.total_tokens -= old.get("token_count", 0)
        while len(self.cache) >= self.max_entries:
            _, old = self.cache.popitem(last=False)
            self.total_tokens -= old.get("token_count", 0)
        kv_state["token_count"] = n; kv_state["cached_at"] = time.time()
        self.cache[key] = kv_state; self.total_tokens += n
    def find_longest_prefix(self, tokens: List[int]) -> Tuple[int, Optional[Dict]]:
        for length in range(len(tokens), 0, -1):
            result = self.get(tokens[:length])
            if result: return length, result
        return 0, None
    def stats(self) -> Dict:
        total = self.hits + self.misses
        return {"entries": len(self.cache), "total_tokens": self.total_tokens,
                "hits": self.hits, "misses": self.misses,
                "hit_rate": f"{self.hits/max(total,1)*100:.1f}%"}
