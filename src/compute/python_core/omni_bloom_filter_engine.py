"""OmniBloomFilterEngine — Production-grade probabilistic set membership.

Implements a Bloom filter using multiple hash functions (SHA-256 derived)
for O(1) insert/query with tunable false positive rate and no false negatives.
"""
import hashlib
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniBloomFilterEngine:
    """Production engine for space-efficient probabilistic set membership."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, expected_items: int = 1000, false_positive_rate: float = 0.01):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive.")
        if not (0 < false_positive_rate < 1):
            raise ValueError("false_positive_rate must be in (0, 1).")

        self.n = expected_items
        self.fp_rate = false_positive_rate
        self.m = self._optimal_size(expected_items, false_positive_rate)
        self.k = self._optimal_hashes(self.m, expected_items)
        self.bit_array = [0] * self.m
        self._count = 0

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        """Compute optimal bit array size: m = -(n * ln(p)) / (ln(2)^2)."""
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return max(int(math.ceil(m)), 64)

    @staticmethod
    def _optimal_hashes(m: int, n: int) -> int:
        """Compute optimal number of hash functions: k = (m/n) * ln(2)."""
        k = (m / n) * math.log(2)
        return max(int(round(k)), 1)

    def _get_hash_indices(self, item: str) -> List[int]:
        """Generate k hash indices using double-hashing via SHA-256."""
        digest = hashlib.sha256(item.encode()).hexdigest()
        h1 = int(digest[:16], 16)
        h2 = int(digest[16:32], 16)
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item: str) -> Result:
        """Add item to the Bloom filter."""
        try:
            indices = self._get_hash_indices(item)
            for idx in indices:
                self.bit_array[idx] = 1
            self._count += 1
            return Ok({"item": item, "added": True, "indices_set": indices})
        except Exception as e:
            return Err(e)

    def contains(self, item: str) -> Result:
        """Check if item is possibly in the set."""
        try:
            indices = self._get_hash_indices(item)
            probably_in = all(self.bit_array[idx] == 1 for idx in indices)
            return Ok({"item": item, "probably_contains": probably_in,
                        "note": "No false negatives; possible false positives." if probably_in else "Definitely not in set."})
        except Exception as e:
            return Err(e)

    def get_stats(self) -> Result:
        """Return filter statistics."""
        filled = sum(self.bit_array)
        actual_fp = (1 - math.exp(-self.k * self._count / self.m)) ** self.k if self.m > 0 else 1.0
        return Ok({"size_bits": self.m, "hash_functions": self.k, "items_added": self._count,
                    "bits_set": filled, "fill_ratio": round(filled / self.m, 6),
                    "estimated_fp_rate": round(actual_fp, 8), "target_fp_rate": self.fp_rate})

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniBloomFilterEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "size_bits": self.m, "hash_functions": self.k}
