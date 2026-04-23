"""OmniPandasDataframeAggregationEngine — Production-grade DataFrame GroupBy aggregation.

Implements the split-apply-combine pattern using pure dictionary-based O(N)
grouping with support for sum, mean, count, min, max aggregations. No external
dataframe library required — operates on raw list-of-dict row format.
"""
import math
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniPandasDataframeAggregationEngine:
    """Production engine for GroupBy aggregation over columnar row data."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, max_rows: int = 100000):
        """
        Initialize aggregation engine.

        Args:
            max_rows: Maximum number of rows accepted for aggregation.
        """
        if max_rows <= 0:
            raise ValueError("max_rows must be positive.")
        self.max_rows = max_rows

    def aggregate_groupby(
        self,
        rows: List[Dict[str, Any]],
        group_key: str,
        value_column: str,
        aggregations: Optional[List[str]] = None,
    ) -> Result:
        """
        Performs split-apply-combine GroupBy aggregation on tabular row data.

        Uses O(N) dictionary accumulation — no sorting required. Supports
        multiple simultaneous aggregation functions per group.

        Args:
            rows: List of row dicts, e.g. [{"city": "NYC", "revenue": 100}, ...]
            group_key: Column name to group by.
            value_column: Column name to aggregate.
            aggregations: List of aggregation names from {"sum", "mean", "count", "min", "max"}.
                          Defaults to ["sum", "mean", "count"].

        Returns:
            Result containing group-level aggregation results.
        """
        try:
            if not rows:
                return Err(ValueError("Row list must be non-empty."))
            if len(rows) > self.max_rows:
                return Err(ValueError(f"Row count {len(rows)} exceeds max_rows={self.max_rows}."))
            if aggregations is None:
                aggregations = ["sum", "mean", "count"]

            valid_aggs = {"sum", "mean", "count", "min", "max"}
            for agg in aggregations:
                if agg not in valid_aggs:
                    return Err(ValueError(f"Unknown aggregation '{agg}'. Valid: {valid_aggs}"))

            # Split phase — accumulate per-group statistics in O(N)
            groups: Dict[str, Dict[str, Any]] = {}

            for row in rows:
                if group_key not in row:
                    return Err(KeyError(f"Missing group_key '{group_key}' in row: {row}"))
                if value_column not in row:
                    return Err(KeyError(f"Missing value_column '{value_column}' in row: {row}"))

                key = str(row[group_key])
                val = float(row[value_column])

                if key not in groups:
                    groups[key] = {"_sum": 0.0, "_count": 0, "_min": math.inf, "_max": -math.inf}

                g = groups[key]
                g["_sum"] += val
                g["_count"] += 1
                if val < g["_min"]:
                    g["_min"] = val
                if val > g["_max"]:
                    g["_max"] = val

            # Apply-combine phase — compute requested aggregations
            results = {}
            for key, g in groups.items():
                entry = {}
                if "sum" in aggregations:
                    entry["sum"] = round(g["_sum"], 6)
                if "mean" in aggregations:
                    entry["mean"] = round(g["_sum"] / g["_count"], 6) if g["_count"] > 0 else 0.0
                if "count" in aggregations:
                    entry["count"] = g["_count"]
                if "min" in aggregations:
                    entry["min"] = g["_min"]
                if "max" in aggregations:
                    entry["max"] = g["_max"]
                results[key] = entry

            return Ok({
                "group_key": group_key,
                "value_column": value_column,
                "aggregations_applied": aggregations,
                "total_rows_processed": len(rows),
                "total_groups": len(results),
                "groups": results,
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniPandasDataframeAggregationEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "max_rows": self.max_rows,
            "complexity": "O(N) split-apply-combine GroupBy aggregation",
        }
