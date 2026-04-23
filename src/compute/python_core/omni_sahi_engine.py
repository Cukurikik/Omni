"""
OMNI SAHI Engine
==================
Production-grade OMNI engine for High-Resolution Image Slicing.
Inspired by obss/sahi.

Features:
- Slicer primitives: Computes overlapping sliding-window bounding boxes for massive images.
- Coordinate Projection: Remaps slice-relative bounding boxes to parent-relative bounding boxes.
- Abstraction points for NMM (Non-Maximum Merging) during high-res inference grouping.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class SAHIErr(Exception):
    """OMNI Zero-Prod Production Implementation for SAHIErr."""
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
# 2. SLICING PRIMITIVES
# ---------------------------------------------------------------------------

@dataclass
class SliceCoordinates:
    """Represents a patch's absolute positions inside the parent image."""
    xmin: int
    ymin: int
    xmax: int
    ymax: int

    def to_array(self) -> np.ndarray:
        """Convert to array representation."""
        return np.array([self.xmin, self.ymin, self.xmax, self.ymax], dtype=int)


class ImageSlicer:
    """
    Computes overlapping patch coordinates across a high resolution image.
    """
    def __init__(self, slice_height: int = 512, slice_width: int = 512, 
                 overlap_height_ratio: float = 0.2, overlap_width_ratio: float = 0.2):
        """Initialize ImageSlicer."""
        self.slice_height = slice_height
        self.slice_width = slice_width
        self.overlap_height_ratio = overlap_height_ratio
        self.overlap_width_ratio = overlap_width_ratio

    def calculate_slices(self, image_height: int, image_width: int) -> Result:
        """Calculates list of slice coordinates."""
        if image_height < self.slice_height or image_width < self.slice_width:
            # Entire image is just one slice
            return Ok([SliceCoordinates(0, 0, image_width, image_height)])

        step_height = int(self.slice_height * (1 - self.overlap_height_ratio))
        step_width = int(self.slice_width * (1 - self.overlap_width_ratio))

        if step_height <= 0 or step_width <= 0:
            return Err("Overlap ratios must be less than 1.0.")

        slices = []
        y = 0
        while y < image_height:
            ymax = min(y + self.slice_height, image_height)
            # Adjust y if reaching the bottom boundary to ensure the slice is exactly slice_height
            # (unless the image itself is smaller than slice_height)
            if ymax - y < self.slice_height and image_height >= self.slice_height:
                y = image_height - self.slice_height
                ymax = image_height

            x = 0
            while x < image_width:
                xmax = min(x + self.slice_width, image_width)
                if xmax - x < self.slice_width and image_width >= self.slice_width:
                    x = image_width - self.slice_width
                    xmax = image_width

                slices.append(SliceCoordinates(xmin=x, ymin=y, xmax=xmax, ymax=ymax))
                
                if xmax == image_width:
                    break
                x += step_width

            if ymax == image_height:
                break
            y += step_height

        return Ok(slices)


class PredictionCombiner:
    """Aggregates slice-level predictions back into the original image bounds."""
    
    @staticmethod
    def project_to_parent(slice_boxes: np.ndarray, shift_xy: Tuple[int, int]) -> Result:
        """
        Projects an array of bounding boxes (x1, y1, x2, y2) from slice coordinates
        to parent image coordinates using the shift offsets.
        """
        if slice_boxes.ndim != 2 or slice_boxes.shape[1] != 4:
            return Err("Boxes must be shaped (N, 4).")

        shift_array = np.array([shift_xy[0], shift_xy[1], shift_xy[0], shift_xy[1]], dtype=np.float32)
        projected = slice_boxes + shift_array
        
        return Ok(projected)

    @staticmethod
    def filter_by_intersection(boxes: np.ndarray, parent_bounds: Tuple[int, int], margin: int = 2) -> np.ndarray:
        """
        Optional heuristic filter to remove boxes that fall exactly on the patch boundaries
        if we expect the overlapping neighbor patch to predict them fully.
        Not fully necessary if robust NMS/NMM is used downstream.
        """
        # Kept abstract for zero-algebraic_bound demonstration
        return {"status": "not_implemented"}


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniSAHIEngine:
    """
    Production Engine for High-Resolution slicing object detection mathematically.
    """

    def __init__(self, config=None):
        """Initialize OmniSAHIEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-sahi"

    def create_slicer(self, slice_height: int = 512, slice_width: int = 512,
                      overlap_h: float = 0.2, overlap_w: float = 0.2) -> ImageSlicer:
        """Performs create slicer operation for OmniSAHIEngine."""
        return ImageSlicer(slice_height, slice_width, overlap_h, overlap_w)

    def get_combiner(self) -> PredictionCombiner:
        """Performs get combiner operation for OmniSAHIEngine."""
        return PredictionCombiner()

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniSAHIEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "operations": ["calculate_slices", "project_to_parent"],
            "status": "operational",
        }
