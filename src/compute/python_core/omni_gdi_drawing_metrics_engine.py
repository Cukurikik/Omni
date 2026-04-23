"""
OMNI GDI Drawing Metrics Engine.
Assimilated from: grantwinney/Surviving-WinForms (Level 2 Abstraction)
Provides: Geometric raster containment math for abstract UI component intersections (WinForms boundary rules).
"""
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "2.0.0-omni-gdi-drawing-metrics"




class OmniGdiDrawingMetricsEngine:
    """
    Execute pixel math collision bounding boxes used by the legacy GDI+ abstraction.
    
    @since 2.0.0
    @tags ["winforms", "gui", "spatial-geometry", "c-sharp"]
    """
    def __init__(self) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        ui_rect = {"x": 50, "y": 50, "w": 100, "h": 100}
        cursor = {"x": 100, "y": 100}
        res = self.check_point_intersection(ui_rect, cursor)
        if res.is_ok() and res.value["is_intersecting"]:
            return Ok({"engine": "GdiDrawingMetrics", "status": "Ready", "raster_math": "Functional"})
        return Err("Raster GDI+ dimension physics calculation failure.")

    def check_point_intersection(self, rectangle: Dict[str, int], point: Dict[str, int]) -> Result:
        """
        Evaluates strict Euclidean limits to test if a point (like a mouse event) landed on a control geometry.
        """
        for k in ["x", "y", "w", "h"]:
             if k not in rectangle:
                  return Err(f"Malformed structural bounding box. Missing geometric property: {k}")
        for k in ["x", "y"]:
             if k not in point:
                  return Err(f"Malformed point locus. Missing axis: {k}")

        rx = rectangle["x"]
        ry = rectangle["y"]
        rw = rectangle["w"]
        rh = rectangle["h"]

        px = point["x"]
        py = point["y"]

        # WinForms point bounds inclusion logic
        inside_x = rx <= px <= (rx + rw)
        inside_y = ry <= py <= (ry + rh)
        
        is_hit = inside_x and inside_y

        return Ok({
            "target_geometry": f"Rectangle({rx},{ry},{rw},{rh})",
            "point_geometry": f"Point({px},{py})",
            "is_intersecting": is_hit
        })
