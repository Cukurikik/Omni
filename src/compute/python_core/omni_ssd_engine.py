"""
OMNI SSD Engine
=================
Production-grade OMNI engine for Object Detection inspired by ssd.pytorch.
Abstracts foundational features:
- IoU (Intersection over Union) mathematical primitives.
- Non-Maximum Suppression (NMS).
- Prior / Anchor Box topological generations.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class SSDErr(Exception):
    """OMNI Zero-Prod Production Implementation for SSDErr."""
    pass

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. SSD PRIMITIVES
# ---------------------------------------------------------------------------

class SSDOperations:
    """Production-grade SSD Operations component."""

    @staticmethod
    def calculate_iou(box1: np.ndarray, box2: np.ndarray) -> np.ndarray:
        """
        Calculate IoU between two arrays of bounding boxes.
        Boxes are formatted as (xmin, ymin, xmax, ymax).
        Supports broadcasting.
        """
        # Determine intersection coordinates
        inner_xmin = np.maximum(box1[..., 0], box2[..., 0])
        inner_ymin = np.maximum(box1[..., 1], box2[..., 1])
        inner_xmax = np.minimum(box1[..., 2], box2[..., 2])
        inner_ymax = np.minimum(box1[..., 3], box2[..., 3])
        
        # Calculate intersection area
        inter_width = np.maximum(0.0, inner_xmax - inner_xmin)
        inter_height = np.maximum(0.0, inner_ymax - inner_ymin)
        inter_area = inter_width * inter_height
        
        # Calculate areas of individual boxes
        box1_area = (box1[..., 2] - box1[..., 0]) * (box1[..., 3] - box1[..., 1])
        box2_area = (box2[..., 2] - box2[..., 0]) * (box2[..., 3] - box2[..., 1])
        
        # Calculate union area
        union_area = box1_area + box2_area - inter_area
        
        # Prevent division by zero
        iou = inter_area / np.maximum(union_area, 1e-10)
        return iou

    @staticmethod
    def non_max_suppression(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float = 0.5) -> Result:
        """
        Greedy Non-Maximum Suppression (NMS).
        boxes: (N, 4) array
        scores: (N,) array
        iou_threshold: threshold above which overlapping boxes are suppressed.
        Returns: Ok(np.ndarray of kept indices)
        """
        if len(boxes) == 0:
            return Ok(np.array([], dtype=int))
            
        if boxes.shape[0] != scores.shape[0]:
            return Err("Number of boxes and scores must match.")
            
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]  # Sort descending

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            
            # Find intersections for all remaining boxes against the top box
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h
            
            # IoU
            ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-10)

            # Keep boxes whose IoU is below threshold
            inds = np.where(ovr <= iou_threshold)[0]
            order = order[inds + 1]

        return Ok(np.array(keep, dtype=int))


class PriorBox:
    """
    Generates anchor grids (Prior Boxes).
    """
    def __init__(self, image_size: int, feature_maps: List[int], min_sizes: List[int], max_sizes: List[int], steps: List[int], clip: bool = True):
        """Initialize PriorBox."""
        self.image_size = image_size
        self.feature_maps = feature_maps
        self.min_sizes = min_sizes
        self.max_sizes = max_sizes
        self.steps = steps
        self.clip = clip

    def forward(self) -> Result:
        """Generate priors based on setup features."""
        try:
            mean = []
            for k, f in enumerate(self.feature_maps):
                for i in range(f):
                    for j in range(f):
                        f_k = self.image_size / self.steps[k]
                        # unit center x,y
                        cx = (j + 0.5) / f_k
                        cy = (i + 0.5) / f_k

                        # aspect_ratio: 1, size: min_size
                        s_k = self.min_sizes[k] / self.image_size
                        mean += [cx, cy, s_k, s_k]

                        # aspect_ratio: 1, size: sqrt(s_k * s_(k+1))
                        s_k_prime = math.sqrt(s_k * (self.max_sizes[k] / self.image_size))
                        mean += [cx, cy, s_k_prime, s_k_prime]

            output = np.array(mean, dtype=np.float32).reshape(-1, 4)
            if self.clip:
                output = np.clip(output, 0.0, 1.0)
            return Ok(output)
        except Exception as e:
            return Err(f"Failed to generate Prior Boxes: {str(e)}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniSSDEngine:
    """
    Production Engine mapping mathematical constants for object detection frameworks.
    """

    def __init__(self, config=None):
        """Initialize OmniSSDEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-ssd"

    def get_operations(self) -> SSDOperations:
        """Performs get operations operation for OmniSSDEngine."""
        return SSDOperations()

    def create_prior_box_generator(self, image_size: int, feature_maps: List[int], min_sizes: List[int], max_sizes: List[int], steps: List[int]) -> PriorBox:
        """Performs create prior box generator operation for OmniSSDEngine."""
        return PriorBox(image_size, feature_maps, min_sizes, max_sizes, steps)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniSSDEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "algorithms": ["IoU", "NMS", "PriorBox"],
            "status": "operational",
        }
