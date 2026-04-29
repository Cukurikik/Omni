import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class ReasonerComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[ReasonerComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class VisualReasonerEngine:
    """
    OMNI Engine: visual-reasoner
    Bounding box Intersection Over Union (IoU) reasoning and spatial relation geometry logic.
    """
    def __init__(self, overlap_threshold: float = 0.5):
        self.overlap_threshold = overlap_threshold

    def compute_spatial_iou(self, box_a: Tuple[float, float, float, float], box_b: Tuple[float, float, float, float]) -> Result:
        # Boxes format [x1, y1, x2, y2]
        try:
            x_left = max(box_a[0], box_b[0])
            y_top = max(box_a[1], box_b[1])
            x_right = min(box_a[2], box_b[2])
            y_bottom = min(box_a[3], box_b[3])
            
            if x_right < x_left or y_bottom < y_top:
                return Result({'iou': 0.0, 'is_intersecting': False})
                
            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            
            box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
            box_b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
            
            if box_a_area <= 0 or box_b_area <= 0:
                 return Result(None, ReasonerComputeError("Point geometries masquerading as volume boxes"))
                 
            iou = intersection_area / float(box_a_area + box_b_area - intersection_area)
            
            return Result({'iou': iou, 'is_intersecting': iou >= self.overlap_threshold})
        except Exception as e:
            return Result(None, ReasonerComputeError(f"Spatial geometry map failed: {str(e)}"))

    def evaluate_relative_position(self, center_a: Tuple[float, float], center_b: Tuple[float, float]) -> Result:
        try:
            dx = center_b[0] - center_a[0]
            dy = center_b[1] - center_a[1]
            
            distance = math.sqrt(dx**2 + dy**2)
            angle_rad = math.atan2(dy, dx)
            
            return Result({'euclidean_distance': distance, 'vector_angle_rad': angle_rad})
        except Exception as e:
            return Result(None, ReasonerComputeError(f"Position mapping divergence: {str(e)}"))
