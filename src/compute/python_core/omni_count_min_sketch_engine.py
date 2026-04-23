"""OmniCountMinSketchEngine — Production-grade Count-Min Sketch.

Implements probabilistic frequency estimation using multiple hash functions
with configurable width and depth for sub-linear space counting.
"""
import hashlib
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniCountMinSketchEngine:
    """Production engine for Count-Min Sketch frequency estimation."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, width: int = 1000, depth: int = 7):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        self._total = 0

    def _hash(self, item: str, i: int) -> int:
        h = hashlib.sha256(f"{i}:{item}".encode()).hexdigest()
        return int(h, 16) % self.width

    def add(self, item: str, count: int = 1) -> Result:
        """Perform add computation.

            Args:
                    item: str
                    count: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            for i in range(self.depth):
                j = self._hash(item, i)
                self.table[i][j] += count
            self._total += count
            return Ok({"added": item, "count": count, "total": self._total})
        except Exception as e:
            return Err(e)

    def estimate(self, item: str) -> Result:
        """Perform estimate computation.

            Args:
                    item: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            est = min(self.table[i][self._hash(item, i)] for i in range(self.depth))
            return Ok({"item": item, "estimated_count": est, "total_items": self._total})
        except Exception as e:
            return Err(e)

    def merge(self, other: 'OmniCountMinSketchEngine') -> Result:
        """Perform merge computation.

            Args:
                    other: 'OmniCountMinSketchEngine'

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if self.width != other.width or self.depth != other.depth:
                return Err(ValueError("Sketches must have same dimensions."))
            for i in range(self.depth):
                for j in range(self.width):
                    self.table[i][j] += other.table[i][j]
            self._total += other._total
            return Ok({"merged": True, "total": self._total})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniCountMinSketchEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "width": self.width, "depth": self.depth,
                "total_items": self._total}
