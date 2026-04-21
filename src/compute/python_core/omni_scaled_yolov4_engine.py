"""
OMNI Scaled YOLOv4 Engine
=========================
Production-grade OMNI engine mathematically managing object detection bounds scaling.
Inspired by WongKinYiu/ScaledYOLOv4.

Features:
- Pure Array bounding box relative scaling computations.
- Hard spatial clipping preventing coordinate extrusion outside image.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"


class ScaledYoloErr(Exception):
    pass


@dataclass(frozen=True)
class Ok:
    value: Any


@dataclass(frozen=True)
class Err:
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. SPATIAL GEOMETRY MAP
# ---------------------------------------------------------------------------

class BoundingBoxMathematics:
    """Implement core matrix bounds anchoring and scaling YOLO coordinates."""

    @staticmethod
    def scale_coords(img1_shape: Tuple[int, int], coords: np.ndarray, img0_shape: Tuple[int, int]) -> np.ndarray:
        """
        Rescales predictions from the inference image structure (img1)
        back to original original image structure (img0).
        coords format: (N, 4) -> [xmin, ymin, xmax, ymax]
        """
        # img shape -> (height, width)
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad_x = (img1_shape[1] - img0_shape[1] * gain) / 2  # wh padding
        pad_y = (img1_shape[0] - img0_shape[0] * gain) / 2
        
        # Transform array
        coords[:, [0, 2]] -= pad_x
        coords[:, [1, 3]] -= pad_y
        coords[:, :4] /= gain
        
        # Geometrical clipping logic safely restricting bounding box escapes
        # Clip X coordinates to [0, original width]
        coords[:, [0, 2]] = np.clip(coords[:, [0, 2]], 0, img0_shape[1])
        # Clip Y coordinates to [0, original height]
        coords[:, [1, 3]] = np.clip(coords[:, [1, 3]], 0, img0_shape[0])
        
        return np.round(coords).astype(int)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniScaledYolov4Engine:
    """
    Production Engine providing spatial coordinate anchor bounding math.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-scaled-yolov4"

    def __init__(self) -> None:
        self._matrices_computed = 0

    def compute_scaled_bounding_boxes(
        self, inference_shape: Tuple[int, int], original_shape: Tuple[int, int], 
        predicted_boxes: List[List[float]]) -> Result:
        """Route structural bounds retrieving normalized pixel mappings."""
        
        if not predicted_boxes:
            return Err("Bounding Box evaluation arrays cannot map empty matrices.")
            
        if inference_shape[0] <= 0 or inference_shape[1] <= 0:
            return Err("Inference image shapes bounded precisely above zero (Height, Width).")
            
        if original_shape[0] <= 0 or original_shape[1] <= 0:
            return Err("Original image shapes bounded precisely above zero (Height, Width).")

        try:
            arr_coords = np.array(predicted_boxes, dtype=np.float64)
            
            if arr_coords.shape[1] < 4:
                return Err("Predicted arrays require [xmin, ymin, xmax, ymax] dimensions.")
                
            scaled = BoundingBoxMathematics.scale_coords(
                img1_shape=inference_shape,
                coords=arr_coords,
                img0_shape=original_shape
            )
            
            self._matrices_computed += 1
            
            return Ok({
                "source_boxes_evaluated": arr_coords.shape[0],
                "scaled_coordinates_xyz": scaled.tolist()
            })
            
        except Exception as exc:
            return Err(f"YOLO scale geometry calculations failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "boxes_scaled": self._matrices_computed,
            "features": [
                "anchor_box_ratio_scaling_math",
                "padding_subtraction_matrix",
                "hard_spatial_coordinate_clipping",
            ]
        }
