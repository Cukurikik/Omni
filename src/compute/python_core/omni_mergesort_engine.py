"""OmniMergesortEngine — Production-grade merge sort with performance metrics.

Implements top-down recursive merge sort with O(N log N) worst-case,
stable sorting, and comparison counting.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMergesortEngine:
    """Production engine for stable merge sort."""

    ENGINE_VERSION = "1.0.0"

    def sort(self, arr: List, key: str = None, reverse: bool = False) -> Result:
        """
        Sort a list using merge sort.

        Args:
            arr: List of comparable items (or dicts if key specified).
            key: Optional dict key for sorting dicts.
            reverse: If True, sort descending.

        Returns:
            Result with sorted list and comparison count.
        """
        try:
            if not arr:
                return Ok({"sorted": [], "comparisons": 0, "length": 0})

            counter = [0]

            def get_val(item):
                return item[key] if key and isinstance(item, dict) else item

            def merge(left, right):
                result = []
                i = j = 0
                while i < len(left) and j < len(right):
                    counter[0] += 1
                    lv, rv = get_val(left[i]), get_val(right[j])
                    if (lv <= rv and not reverse) or (lv >= rv and reverse):
                        result.append(left[i])
                        i += 1
                    else:
                        result.append(right[j])
                        j += 1
                result.extend(left[i:])
                result.extend(right[j:])
                return result

            def merge_sort(a):
                if len(a) <= 1:
                    return a
                mid = len(a) // 2
                left = merge_sort(a[:mid])
                right = merge_sort(a[mid:])
                return merge(left, right)

            sorted_arr = merge_sort(list(arr))
            return Ok({"sorted": sorted_arr, "comparisons": counter[0], "length": len(sorted_arr),
                        "stable": True, "reverse": reverse})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMergesortEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log N) worst-case stable"}
