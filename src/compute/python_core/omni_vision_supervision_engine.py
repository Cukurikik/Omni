# ===========================================================================
# OMNI VISION SUPERVISION ENGINE (SEMESTER 5 — BATCH 9)
# ===========================================================================
# Absorbed From  : roboflow/supervision
# Logic Inherited: Compute Layer (Pure Geometry BBox Processing)
# ===========================================================================
"""
OMNI Vision Supervision Engine
==============================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
from typing import Dict, Any, Tuple, List


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

logger = logging.getLogger("OmniVisionSupervisionEngine")

class OmniVisionSupervisionEngine:
    """
    Pure geometric operations for CV outputs: IoU calculation,
    ray-casting polygon zone detection. No OpenCV dependency.
    """

    def __init__(self):
        """Initialize OmniVisionSupervisionEngine."""
        self._is_ready = True

    def calculate_iou(self, a: Tuple[float,float,float,float], b: Tuple[float,float,float,float]) -> Dict[str, Any]:
        """Calculates Intersection over Union between two bounding boxes (x1,y1,x2,y2)."""
        ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
        ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
        inter = max(0, ix2-ix1) * max(0, iy2-iy1)
        area_a = max(0, a[2]-a[0]) * max(0, a[3]-a[1])
        area_b = max(0, b[2]-b[0]) * max(0, b[3]-b[1])
        union = area_a + area_b - inter
        iou = inter / union if union > 0 else 0.0
        return {"status": "success", "data": {"iou": round(iou, 4), "intersection": round(inter, 2), "union": round(union, 2)}}

    def check_point_in_polygon(self, point: Tuple[float,float], polygon: List[Tuple[float,float]]) -> Dict[str, Any]:
        """Ray-casting algorithm for point-in-polygon detection."""
        if len(polygon) < 3:
            return {"status": "error", "error": "Polygon needs ≥ 3 vertices."}
        x, y = point
        inside = False
        n = len(polygon)
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y:
                    xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xints:
                    inside = not inside
            p1x, p1y = p2x, p2y
        return {"status": "success", "data": {"is_inside": inside, "point": point}}

    def evaluate_health(self) -> Dict[str, Any]:
        """Performs evaluate health operation for OmniVisionSupervisionEngine."""
        return {"engine": "OmniVisionSupervisionEngine", "layer": "Compute", "status": "healthy",
                "capabilities": ["IoU", "Polygon Zone Detection"], "learned_from": "roboflow/supervision"}

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-vision-supervision",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
