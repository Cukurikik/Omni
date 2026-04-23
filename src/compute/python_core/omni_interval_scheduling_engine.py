"""OmniIntervalSchedulingEngine — Production-grade interval scheduling optimizer.

Implements greedy interval scheduling maximization (activity selection),
interval merging, and conflict detection for time-based resource allocation.
"""
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniIntervalSchedulingEngine:
    """Production engine for interval scheduling optimization."""

    ENGINE_VERSION = "1.0.0"

    def maximize_non_overlapping(self, intervals: List[Tuple[float, float]]) -> Result:
        """Greedy activity selection: maximize number of non-overlapping intervals."""
        try:
            if not intervals:
                return Err(ValueError("Intervals must be non-empty."))
            indexed = sorted(enumerate(intervals), key=lambda x: x[1][1])
            selected = [indexed[0]]
            for i in range(1, len(indexed)):
                if indexed[i][1][0] >= selected[-1][1][1]:
                    selected.append(indexed[i])
            return Ok({"selected": [{"index": s[0], "start": s[1][0], "end": s[1][1]} for s in selected],
                        "count": len(selected), "total_intervals": len(intervals)})
        except Exception as e:
            return Err(e)

    def merge_overlapping(self, intervals: List[Tuple[float, float]]) -> Result:
        """Merge all overlapping intervals."""
        try:
            if not intervals:
                return Ok({"merged": [], "count": 0})
            sorted_ivs = sorted(intervals, key=lambda x: x[0])
            merged = [list(sorted_ivs[0])]
            for start, end in sorted_ivs[1:]:
                if start <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], end)
                else:
                    merged.append([start, end])
            return Ok({"merged": [{"start": m[0], "end": m[1]} for m in merged],
                        "count": len(merged), "original_count": len(intervals),
                        "merges_performed": len(intervals) - len(merged)})
        except Exception as e:
            return Err(e)

    def find_conflicts(self, intervals: List[Tuple[float, float]]) -> Result:
        """Find all pairs of conflicting (overlapping) intervals."""
        try:
            conflicts = []
            n = len(intervals)
            for i in range(n):
                for j in range(i + 1, n):
                    a, b = intervals[i], intervals[j]
                    if a[0] < b[1] and b[0] < a[1]:
                        conflicts.append({"pair": [i, j], "intervals": [list(a), list(b)]})
            return Ok({"conflicts": conflicts, "conflict_count": len(conflicts), "total_intervals": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniIntervalSchedulingEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log N) greedy scheduling"}
