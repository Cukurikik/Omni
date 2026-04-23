"""OmniParallelMergeSortEngine simulating tracking of parallel merge sort execution."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniParallelMergeSortEngine(OmniBaseEngine):
    """Production-grade Omni Parallel Merge Sort Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self):
        self.max_depth = 0

    def sort(self, data: List[float]) -> Result[Dict[str, Any], str]:
        """
        Sorts the array deteministically while calculating the 'parallel' tree depth.
        """
        try:
            self.max_depth = 0
            if not data:
                return Result.ok({"sorted": [], "max_tree_depth": 0})
                
            sorted_arr = self._parallel_merge_sort(data, 1)
            
            return Result.ok({
                "sorted": sorted_arr,
                "max_tree_depth": self.max_depth
            })
        except Exception as e:
            return Result.fail(str(e))

    def _parallel_merge_sort(self, arr: List[float], depth: int) -> List[float]:
        if depth > self.max_depth:
            self.max_depth = depth
            
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        
        # Simulate parallel branching
        left = self._parallel_merge_sort(arr[:mid], depth + 1)
        right = self._parallel_merge_sort(arr[mid:], depth + 1)

        return self._merge(left, right)

    def _merge(self, left: List[float], right: List[float]) -> List[float]:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(float(left[i]))
                i += 1
            else:
                result.append(float(right[j]))
                j += 1
                
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniParallelMergeSortEngine",
            "status": "operational",
            "complexity": "O(N log N)"
        }
