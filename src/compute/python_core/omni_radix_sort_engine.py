"""OmniRadixSortEngine — Production-grade radix sort (LSD).

Implements Least Significant Digit radix sort with counting sort subroutine
for O(d*(N+k)) non-comparison integer sorting.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniRadixSortEngine:
    """Production engine for LSD radix sort."""

    ENGINE_VERSION = "1.0.0"

    def sort(self, data: List[int], base: int = 10) -> Result:
        """Perform sort computation.

            Args:
                    data: List[int]
                    base: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not data:
                return Ok({"sorted": [], "length": 0, "passes": 0})
            negatives = [x for x in data if x < 0]
            positives = [x for x in data if x >= 0]
            sorted_pos = self._lsd_sort(positives, base) if positives else []
            sorted_neg = [-x for x in self._lsd_sort([-x for x in negatives], base)] if negatives else []
            sorted_neg.reverse()
            result = sorted_neg + sorted_pos
            max_val = max(abs(x) for x in data) if data else 0
            passes = 0
            v = max_val
            while v > 0:
                passes += 1
                v //= base
            return Ok({"sorted": result, "length": len(result), "passes": max(passes, 1), "base": base})
        except Exception as e:
            return Err(e)

    def _lsd_sort(self, arr: List[int], base: int) -> List[int]:
        if not arr:
            return []
        max_val = max(arr)
        exp = 1
        output = list(arr)
        while max_val // exp > 0:
            count = [0] * base
            for x in output:
                count[(x // exp) % base] += 1
            for i in range(1, base):
                count[i] += count[i - 1]
            result = [0] * len(output)
            for x in reversed(output):
                digit = (x // exp) % base
                count[digit] -= 1
                result[count[digit]] = x
            output = result
            exp *= base
        return output

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniRadixSortEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(d*(N+k)) LSD radix sort"}
