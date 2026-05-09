"""
moe_routing_cache.py — Compute / Optimization
Layer: Compute / AI — Deterministic Routing Cache

For tasks like prompt evaluation or structured generation, routing decisions
should ideally be deterministic. This module caches the router's assignment
for a specific input embedding, allowing the system to skip the router's
forward pass entirely on subsequent identical queries.
"""
import torch
import hashlib
from typing import Dict, Tuple

class MoERoutingCache:
    """
    Caches token-to-expert assignments to save compute on identical prompts.
    """
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.cache: Dict[str, torch.Tensor] = {}
        
    def _hash_tensor(self, tensor: torch.Tensor) -> str:
        """
        Creates a fast hash of the tensor data.
        In reality, we might hash the input IDs instead of the floating point embeddings
        to avoid precision issues.
        """
        # Convert a subset of the tensor to bytes for hashing
        tensor_bytes = tensor.detach().cpu().numpy().tobytes()
        return hashlib.md5(tensor_bytes).hexdigest()

    def get_cached_routing(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Attempts to retrieve cached routing weights.
        Returns None if a cache miss occurs.
        """
        key = self._hash_tensor(embeddings)
        return self.cache.get(key, None)

    def cache_routing(self, embeddings: torch.Tensor, routing_weights: torch.Tensor):
        """
        Saves the routing decision for future lookups.
        """
        if len(self.cache) >= self.max_entries:
            # Simple FIFO eviction (pop first item)
            first_key = next(iter(self.cache))
            self.cache.pop(first_key)
            
        key = self._hash_tensor(embeddings)
        self.cache[key] = routing_weights.detach().clone()

# Example usage inside MoE Layer:
# cache = MoERoutingCache()
#
# cached_weights = cache.get_cached_routing(x)
# if cached_weights is not None:
#     weights = cached_weights
# else:
#     weights = router(x)
#     cache.cache_routing(x, weights)
