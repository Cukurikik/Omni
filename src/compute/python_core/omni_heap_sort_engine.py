"""OmniHeapSortEngine — Production-grade heap sort.

Implements in-place heap sort using max-heap for O(N log N) worst-case sorting.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniHeapSortEngine:
    """Production engine for heap sort algorithm."""

    ENGINE_VERSION = "1.0.0"

    def sort(self, data: List, reverse: bool = False) -> Result:
        """Perform sort computation.

            Args:
                    data: List
                    reverse: bool

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            arr = list(data)
            n = len(arr)
            swaps = [0]
            for i in range(n // 2 - 1, -1, -1):
                self._heapify(arr, n, i, swaps)
            for i in range(n - 1, 0, -1):
                arr[0], arr[i] = arr[i], arr[0]
                swaps[0] += 1
                self._heapify(arr, i, 0, swaps)
            if reverse:
                arr.reverse()
            return Ok({"sorted": arr, "length": n, "swaps": swaps[0], "algorithm": "heapsort"})
        except Exception as e:
            return Err(e)

    def _heapify(self, arr, n, i, swaps):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            swaps[0] += 1
            self._heapify(arr, n, largest, swaps)

    def build_heap(self, data: List) -> Result:
        """Perform build heap computation.

            Args:
                    data: List

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            arr = list(data)
            n = len(arr)
            for i in range(n // 2 - 1, -1, -1):
                self._heapify(arr, n, i, [0])
            return Ok({"heap": arr, "length": n, "is_max_heap": True})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniHeapSortEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log N) worst-case"}
