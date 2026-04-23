"""OmniEventCapacityOptimizerEngine for optimal event seating allocations."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniEventCapacityOptimizerEngine(OmniBaseEngine):
    """Production-grade Omni Event Capacity Optimizer Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def optimize(self, capacity: int, groups: List[Dict[str, int]]) -> Result[Dict[str, Any], str]:
        """
        Maximizes total attendee count and/or value under a hard capacity limit using 0/1 Knapsack logic.
        Groups must have 'size' and 'value'.
        """
        try:
            if capacity < 0:
                return Result.fail("Capacity cannot be negative")

            n = len(groups)
            # dp[i][w] logic -> 1D array to save space
            dp = [0] * (capacity + 1)
            keep = [[False] * (capacity + 1) for _ in range(n)]

            for i in range(1, n + 1):
                size = groups[i-1].get('size', 0)
                val = groups[i-1].get('value', 0)
                
                if size < 0 or val < 0:
                    return Result.fail("Size and value must be non-negative")

                for w in range(capacity, size - 1, -1):
                    if dp[w - size] + val > dp[w]:
                        dp[w] = dp[w - size] + val
                        keep[i-1][w] = True

            # Reconstruct choice
            chosen_indices = []
            curr_cap = capacity
            for i in range(n - 1, -1, -1):
                if keep[i][curr_cap]:
                    chosen_indices.append(i)
                    curr_cap -= groups[i]['size']

            chosen_indices.reverse()
            total_size = sum(groups[idx]['size'] for idx in chosen_indices)

            return Result.ok({
                "maximized_value": dp[capacity],
                "total_size_used": total_size,
                "chosen_indices": chosen_indices
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniEventCapacityOptimizerEngine",
            "status": "operational",
            "complexity": "O(N * Capacity)"
        }
