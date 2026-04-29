import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class SketchComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[SketchComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class SketchThinkerEngine:
    """
    OMNI Engine: SketchThinker-R1
    Linear mapping logic for sketching stroke geometry and MLLM reasoning alignment.
    """
    def __init__(self, stroke_simplification_tolerance: float = 2.5):
        self.tolerance = stroke_simplification_tolerance

    def _euclidean_dist(self, p1: np.ndarray, p2: np.ndarray) -> float:
        return float(np.linalg.norm(p1 - p2))

    def evaluate_stroke_complexity(self, stroke_points: np.ndarray) -> Result:
        try:
            if len(stroke_points.shape) != 2 or stroke_points.shape[1] != 2:
                return Result(None, SketchComputeError("Stroke tensor must be [N, 2] Cartesian coordinates"))
                
            n_points = stroke_points.shape[0]
            if n_points < 2:
                return Result(None, SketchComputeError("Degenerate geometric stroke (requires >= 2 points)"))
                
            total_length = 0.0
            for i in range(1, n_points):
                total_length += self._euclidean_dist(stroke_points[i], stroke_points[i-1])
                
            bounding_box_area = (np.max(stroke_points[:,0]) - np.min(stroke_points[:,0])) * \
                                (np.max(stroke_points[:,1]) - np.min(stroke_points[:,1]))
                                
            if bounding_box_area == 0.0:
                 return Result(None, SketchComputeError("Stroke is a perfect mathematical 1D line or singularity constraint breached"))
                 
            complexity_ratio = total_length / math.sqrt(bounding_box_area)
            
            return Result({'stroke_length': total_length, 'complexity_ratio': complexity_ratio})
        except Exception as e:
            return Result(None, SketchComputeError(f"Stroke processing fault: {str(e)}"))

    def compute_cognitive_reasoning_gap(self, intended_angle: float, drawn_angle: float) -> Result:
        try:
            gap = abs(intended_angle - drawn_angle)
            if gap > math.pi:
                gap = 2 * math.pi - gap
                
            is_aligned = bool(gap <= self.tolerance * (math.pi / 180.0))
            return Result({'angular_divergence_rads': gap, 'is_aligned_to_reasoning': is_aligned})
        except Exception as e:
            return Result(None, SketchComputeError(f"Reasoning gap eval failed: {str(e)}"))
