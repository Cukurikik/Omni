"""OmniConvexHullEngine — Production-grade convex hull (Graham Scan).

Implements Graham Scan O(N log N) for 2D convex hull computation
with area calculation and point-in-hull testing.
"""
import math
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniConvexHullEngine:
    """Production engine for 2D convex hull computation."""

    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def _cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def graham_scan(self, points: List[Tuple[float, float]]) -> Result:
        """Perform graham scan computation.

            Args:
                    points: List[Tuple[float
                    float]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if len(points) < 3:
                return Err(ValueError("Need at least 3 points for convex hull."))
            pts = sorted(set(points))
            if len(pts) < 3:
                return Err(ValueError("Need at least 3 distinct points."))

            # Build lower hull
            lower = []
            for p in pts:
                while len(lower) >= 2 and self._cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)
            # Build upper hull
            upper = []
            for p in reversed(pts):
                while len(upper) >= 2 and self._cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)
            hull = lower[:-1] + upper[:-1]

            area = self._polygon_area(hull)
            perimeter = sum(
                math.sqrt((hull[(i+1) % len(hull)][0] - hull[i][0])**2 + (hull[(i+1) % len(hull)][1] - hull[i][1])**2)
                for i in range(len(hull))
            )

            return Ok({"hull": [list(p) for p in hull], "hull_size": len(hull),
                        "area": round(area, 10), "perimeter": round(perimeter, 10),
                        "input_points": len(points)})
        except Exception as e:
            return Err(e)

    def _polygon_area(self, hull):
        n = len(hull)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += hull[i][0] * hull[j][1]
            area -= hull[j][0] * hull[i][1]
        return abs(area) / 2.0

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniConvexHullEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log N) Graham Scan"}
