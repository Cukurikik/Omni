"""OMNI Compute — Reformer (Locality-Sensitive Hashing Attention)"""
import logging
import math
from typing import List

logger = logging.getLogger("omni.reformer")

class LSHAttention:
    """
    Implements Locality-Sensitive Hashing (LSH) Attention for Reformer.
    Reduces attention complexity from O(L^2) to O(L log L).
    """
    def __init__(self, d_model: int, num_hashes: int = 8, bucket_size: int = 64):
        self.d_model = d_model
        self.num_hashes = num_hashes
        self.bucket_size = bucket_size
        logger.info(f"Initialized LSH Attention (hashes={num_hashes}, bucket={bucket_size})")

    def _hash_vectors(self, vectors: List[List[float]]) -> List[int]:
        """Simulates random projection hashing."""
        hashes = []
        for v in vectors:
            # Simple heuristic hash based on vector sum
            h = int(sum(v) * 100) % self.num_hashes
            hashes.append(h)
        return hashes

    def forward(self, queries: List[List[float]], keys: List[List[float]], values: List[List[float]]) -> List[List[float]]:
        """LSH Attention forward pass."""
        seq_len = len(queries)
        if seq_len == 0: return []
        
        # Hash queries and keys (in Reformer Q=K)
        q_hashes = self._hash_vectors(queries)
        
        # Group by hash bucket
        buckets = {i: [] for i in range(self.num_hashes)}
        for idx, h in enumerate(q_hashes):
            buckets[h].append(idx)
            
        output = [[0.0]*self.d_model for _ in range(seq_len)]
        
        # Attention within buckets
        for h, indices in buckets.items():
            for i in indices:
                context = [0.0]*self.d_model
                weight_sum = 0.0
                for j in indices:
                    # Dot product
                    dot = sum(queries[i][d] * keys[j][d] for d in range(self.d_model))
                    w = math.exp(dot / math.sqrt(self.d_model))
                    weight_sum += w
                    for d in range(self.d_model):
                        context[d] += w * values[j][d]
                
                if weight_sum > 0:
                    output[i] = [c / weight_sum for c in context]
                    
        return output
