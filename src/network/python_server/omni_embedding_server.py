"""
OMNI Network — High-Performance Embedding Server
Async embedding inference with batching and caching.
"""
import hashlib, json, time, logging, asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger("omni.embed_server")

@dataclass
class EmbeddingRequest:
    texts: List[str]; model: str = "omni-embed-v2"; request_id: str = ""

@dataclass
class EmbeddingResponse:
    embeddings: List[List[float]]; model: str; latency_ms: float
    total_tokens: int = 0; request_id: str = ""

class EmbeddingCache:
    """LRU cache for embeddings."""
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size; self._cache: Dict[str, List[float]] = {}
        self._order: List[str] = []; self.hits = 0; self.misses = 0
    def _key(self, text: str, model: str) -> str:
        return hashlib.md5(f"{model}:{text}".encode()).hexdigest()
    def get(self, text: str, model: str) -> Optional[List[float]]:
        k = self._key(text, model)
        if k in self._cache:
            self.hits += 1; self._order.remove(k); self._order.append(k)
            return self._cache[k]
        self.misses += 1; return None
    def put(self, text: str, model: str, embedding: List[float]):
        k = self._key(text, model)
        if len(self._cache) >= self.max_size:
            old = self._order.pop(0); del self._cache[old]
        self._cache[k] = embedding; self._order.append(k)
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / max(total, 1)

class DynamicBatcher:
    """Dynamic request batching for throughput."""
    def __init__(self, max_batch: int = 32, max_wait_ms: float = 50.0):
        self.max_batch = max_batch; self.max_wait = max_wait_ms / 1000.0
        self._queue: List = []; self._lock = asyncio.Lock()
    async def add(self, texts: List[str]) -> asyncio.Future:
        future = asyncio.get_event_loop().create_future()
        async with self._lock:
            self._queue.append((texts, future))
        return future

class OmniEmbeddingServer:
    """Production embedding inference server."""
    def __init__(self, embed_fn=None, cache_size: int = 10000, max_batch: int = 32):
        self.embed_fn = embed_fn or self._default_embed
        self.cache = EmbeddingCache(cache_size)
        self.batcher = DynamicBatcher(max_batch)
        self.stats = {"total_requests": 0, "total_texts": 0, "total_latency": 0.0}
    def _default_embed(self, texts: List[str]) -> List[List[float]]:
        import random
        return [[random.gauss(0, 0.1) for _ in range(384)] for _ in texts]
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        start = time.time()
        self.stats["total_requests"] += 1
        self.stats["total_texts"] += len(request.texts)
        results = [None] * len(request.texts)
        uncached_indices, uncached_texts = [], []
        for i, text in enumerate(request.texts):
            cached = self.cache.get(text, request.model)
            if cached: results[i] = cached
            else: uncached_indices.append(i); uncached_texts.append(text)
        if uncached_texts:
            new_embeds = self.embed_fn(uncached_texts)
            for idx, text, emb in zip(uncached_indices, uncached_texts, new_embeds):
                results[idx] = emb; self.cache.put(text, request.model, emb)
        latency = (time.time() - start) * 1000
        self.stats["total_latency"] += latency
        return EmbeddingResponse(embeddings=results, model=request.model,
                                  latency_ms=round(latency, 2), request_id=request.request_id)
    def get_stats(self) -> Dict:
        avg = self.stats["total_latency"] / max(self.stats["total_requests"], 1)
        return {**self.stats, "avg_latency_ms": round(avg, 2),
                "cache_hit_rate": round(self.cache.hit_rate, 4)}
