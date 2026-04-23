from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniFast2DGameEngine:
    """
    omni-fast-2d-game-engine
    
    A native matrix bounding computationally execute AABB Axis-Aligned Bounding Box
    collision mathematics natively mirroring core logic loops of fast 2D rendering systems.
    """
    
    ENGINE_VERSION = "omni-s11-b7.1.0"
    
    def __init__(self, frame_time_ms_target: float = 16.67) -> None:
        self.frame_target = frame_time_ms_target

    def compute_aabb_collisions(self, sprite_a: Dict[str, float], sprite_b: Dict[str, float]) -> Result:
        """
        Natively isolates bounding array overlap structures calculating true mathematics limit.
        Sprite format: {"x": 10.0, "y": 10.0, "width": 5.0, "height": 5.0, "id": 1}
        """
        try:
            for required in ["x", "y", "width", "height", "id"]:
                if required not in sprite_a or required not in sprite_b:
                    return Err(ValueError(f"Mathematical bounds limit dimension mismatch: Missing {required} property in AABB Matrix."))
                    
            if sprite_a["width"] < 0 or sprite_a["height"] < 0 or sprite_b["width"] < 0 or sprite_b["height"] < 0:
                return Err(ValueError("Geometrical bounds size limit must computationally exceed zero dimensions!"))
                
            # AABB mathematics natively limits boundaries overlaps!
            overlaps_x = sprite_a["x"] < sprite_b["x"] + sprite_b["width"] and sprite_a["x"] + sprite_a["width"] > sprite_b["x"]
            overlaps_y = sprite_a["y"] < sprite_b["y"] + sprite_b["height"] and sprite_a["y"] + sprite_a["height"] > sprite_b["y"]
            
            is_intersecting = overlaps_x and overlaps_y
            
            # Simulated mathematical boundaries
            return Ok({
                "collision_detected": is_intersecting,
                "intersection_axes": {
                    "x_axis_overlap": overlaps_x,
                    "y_axis_overlap": overlaps_y
                },
                "entities_checked": [sprite_a["id"], sprite_b["id"]]
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides native topology bounds verifications limit bounds."""
        return {
            "engine": "OmniFast2DGameEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "fps_target_bound": round(1000.0 / self.frame_target, 2),
            "complexity": "O(1) Geometric Algebraic Matrix Boundaries"
        }
