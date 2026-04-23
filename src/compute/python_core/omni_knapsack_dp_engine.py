"""OmniKnapsackDynamicProgrammingEngine — 0/1 Knapsack solver via DP.

Implements the classic O(N*W) bottom-up DP solution with item traceback
for the 0/1 Knapsack problem.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniKnapsackDynamicProgrammingEngine:
    """Production engine for 0/1 Knapsack problem via dynamic programming."""

    ENGINE_VERSION = "1.0.0"

    def solve(self, weights: List[int], values: List[int], capacity: int) -> Result:
        """
        Solve 0/1 Knapsack problem.

        Args:
            weights: List of item weights.
            values: List of item values.
            capacity: Maximum knapsack capacity.

        Returns:
            Result with max value, selected items, and DP table dimensions.
        """
        try:
            n = len(weights)
            if n != len(values):
                return Err(ValueError("weights and values must have equal length."))
            if capacity < 0:
                return Err(ValueError("Capacity must be non-negative."))
            if any(w < 0 for w in weights):
                return Err(ValueError("Weights must be non-negative."))

            dp = [[0] * (capacity + 1) for _ in range(n + 1)]

            for i in range(1, n + 1):
                for w in range(capacity + 1):
                    dp[i][w] = dp[i - 1][w]
                    if weights[i - 1] <= w:
                        dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])

            # Traceback selected items
            selected = []
            w = capacity
            for i in range(n, 0, -1):
                if dp[i][w] != dp[i - 1][w]:
                    selected.append(i - 1)
                    w -= weights[i - 1]
            selected.reverse()

            total_weight = sum(weights[i] for i in selected)

            return Ok({"max_value": dp[n][capacity], "selected_items": selected,
                        "total_weight": total_weight, "capacity": capacity,
                        "n_items": n, "utilization": round(total_weight / capacity, 6) if capacity > 0 else 0.0})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniKnapsackDynamicProgrammingEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N*W) bottom-up DP"}
