"""OmniQuicksortEngine — Production-grade quicksort with median-of-three pivot.

Implements in-place quicksort with median-of-three pivot selection,
3-way partitioning for duplicate handling, and insertion sort fallback for small arrays.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniQuicksortEngine:
    """Production engine for quicksort with median-of-three pivot."""

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
            comparisons = [0]
            self._quicksort(arr, 0, len(arr) - 1, comparisons)
            if reverse:
                arr.reverse()
            return Ok({"sorted": arr, "length": len(arr), "comparisons": comparisons[0], "algorithm": "quicksort-median3"})
        except Exception as e:
            return Err(e)

    def _median_of_three(self, arr, lo, hi):
        mid = (lo + hi) // 2
        if arr[lo] > arr[mid]:
            arr[lo], arr[mid] = arr[mid], arr[lo]
        if arr[lo] > arr[hi]:
            arr[lo], arr[hi] = arr[hi], arr[lo]
        if arr[mid] > arr[hi]:
            arr[mid], arr[hi] = arr[hi], arr[mid]
        arr[mid], arr[hi - 1] = arr[hi - 1], arr[mid]
        return arr[hi - 1]

    def _insertion_sort(self, arr, lo, hi, comps):
        for i in range(lo + 1, hi + 1):
            key = arr[i]
            j = i - 1
            while j >= lo and arr[j] > key:
                comps[0] += 1
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key

    def _quicksort(self, arr, lo, hi, comps):
        if hi - lo < 10:
            self._insertion_sort(arr, lo, hi, comps)
            return
        pivot = self._median_of_three(arr, lo, hi)
        lt, gt = lo, hi - 1
        i = lo
        while i <= gt:
            comps[0] += 1
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[gt], arr[i] = arr[i], arr[gt]
                gt -= 1
            else:
                i += 1
        self._quicksort(arr, lo, lt - 1, comps)
        self._quicksort(arr, gt + 1, hi, comps)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniQuicksortEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log N) avg, median-of-three pivot"}
