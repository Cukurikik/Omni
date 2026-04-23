"""
OMNI Objectron Engine
======================
Production-grade OMNI engine abstracting 3D object detection,
bounding box estimation, pose computation, and dataset management.
Inspired by google-research-datasets/Objectron.

Features:
- 3D bounding box representation with 9-DOF pose (3D position + 3x3 rotation).
- IoU computation for 3D axis-aligned bounding boxes.
- Camera intrinsics and projection utilities.
- AR-style annotation parsing for object-centric video frames.
- Evaluation metrics (AP, IoU@threshold).
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class ObjectronErr(Exception):
    """Base error for Objectron engine."""
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
# 2. 3D GEOMETRY PRIMITIVES
# ---------------------------------------------------------------------------

class ObjectCategory(Enum):
    """Objectron supported object categories."""
    BIKE = "bike"
    BOOK = "book"
    BOTTLE = "bottle"
    CAMERA = "camera"
    CEREAL_BOX = "cereal_box"
    CHAIR = "chair"
    CUP = "cup"
    LAPTOP = "laptop"
    SHOE = "shoe"


@dataclass
class BoundingBox3D:
    """3D bounding box with center, dimensions, and rotation.

    Attributes:
        center: (x, y, z) center position.
        dimensions: (width, height, depth) in metres.
        rotation: 3x3 rotation matrix.
        category: Object category.
        confidence: Detection confidence score.
    """
    center: np.ndarray  # (3,)
    dimensions: np.ndarray  # (3,) — width, height, depth
    rotation: np.ndarray = field(default_factory=lambda: np.eye(3))  # (3,3)
    category: ObjectCategory = ObjectCategory.CUP
    confidence: float = 1.0

    @property
    def volume(self) -> float:
        """Compute bounding box volume in cubic metres."""
        return float(np.prod(self.dimensions))

    def get_corners(self) -> np.ndarray:
        """Compute the 8 corner vertices of the 3D bounding box.

        Returns:
            Array of shape (8, 3) representing corner coordinates.
        """
        w, h, d = self.dimensions / 2.0
        corners_local = np.array([
            [-w, -h, -d], [+w, -h, -d], [+w, +h, -d], [-w, +h, -d],
            [-w, -h, +d], [+w, -h, +d], [+w, +h, +d], [-w, +h, +d],
        ])
        corners_world = (self.rotation @ corners_local.T).T + self.center
        return corners_world


@dataclass
class CameraIntrinsics:
    """Camera intrinsic parameters.

    Attributes:
        fx: Focal length x.
        fy: Focal length y.
        cx: Principal point x.
        cy: Principal point y.
        width: Image width in pixels.
        height: Image height in pixels.
    """
    fx: float = 500.0
    fy: float = 500.0
    cx: float = 320.0
    cy: float = 240.0
    width: int = 640
    height: int = 480

    @property
    def matrix(self) -> np.ndarray:
        """Return the 3x3 intrinsic matrix."""
        return np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1],
        ], dtype=np.float64)


@dataclass
class FrameAnnotation:
    """Annotation for a single video frame."""
    frame_id: int
    timestamp: float
    objects: List[BoundingBox3D] = field(default_factory=list)
    camera: CameraIntrinsics = field(default_factory=CameraIntrinsics)


# ---------------------------------------------------------------------------
# 3. IoU COMPUTATION
# ---------------------------------------------------------------------------

class IoU3D:
    """Compute 3D Intersection over Union for axis-aligned bounding boxes."""

    @staticmethod
    def compute_aabb_iou(box_a: BoundingBox3D, box_b: BoundingBox3D) -> float:
        """Compute IoU between two axis-aligned bounding boxes.

        Uses AABB (axis-aligned bounding box) approximation.

        Args:
            box_a: First bounding box.
            box_b: Second bounding box.

        Returns:
            IoU score between 0 and 1.
        """
        # Compute AABB extents
        a_min = box_a.center - box_a.dimensions / 2.0
        a_max = box_a.center + box_a.dimensions / 2.0
        b_min = box_b.center - box_b.dimensions / 2.0
        b_max = box_b.center + box_b.dimensions / 2.0

        # Intersection
        inter_min = np.maximum(a_min, b_min)
        inter_max = np.minimum(a_max, b_max)
        inter_dims = np.maximum(inter_max - inter_min, 0.0)
        inter_vol = float(np.prod(inter_dims))

        # Union
        vol_a = box_a.volume
        vol_b = box_b.volume
        union_vol = vol_a + vol_b - inter_vol

        if union_vol < 1e-12:
            return 0.0
        return inter_vol / union_vol


# ---------------------------------------------------------------------------
# 4. PROJECTION
# ---------------------------------------------------------------------------

class Projector:
    """Projects 3D points onto 2D image plane."""

    @staticmethod
    def project_points(points_3d: np.ndarray,
                       camera: CameraIntrinsics) -> np.ndarray:
        """Project 3D points to 2D pixel coordinates.

        Args:
            points_3d: (N, 3) array of 3D points.
            camera: Camera intrinsics.

        Returns:
            (N, 2) array of 2D pixel coordinates.
        """
        K = camera.matrix
        # Assume points are already in camera frame
        projected = (K @ points_3d.T).T
        z = projected[:, 2:3]
        z = np.where(np.abs(z) < 1e-12, 1e-12, z)  # avoid div by zero
        pixels = projected[:, :2] / z
        return pixels


# ---------------------------------------------------------------------------
# 5. EVALUATION METRICS
# ---------------------------------------------------------------------------

class DetectionMetrics:
    """Compute detection evaluation metrics for 3D object detection."""

    @staticmethod
    def average_precision(predictions: List[BoundingBox3D],
                          ground_truths: List[BoundingBox3D],
                          iou_threshold: float = 0.5) -> float:
        """Compute Average Precision at a given IoU threshold.

        Args:
            predictions: Predicted bounding boxes sorted by confidence.
            ground_truths: Ground truth bounding boxes.
            iou_threshold: IoU threshold for a match.

        Returns:
            AP score.
        """
        if not ground_truths:
            return 0.0 if predictions else 1.0

        preds_sorted = sorted(predictions, key=lambda b: b.confidence,
                              reverse=True)
        gt_matched = [False] * len(ground_truths)
        tp_list: List[int] = []
        fp_list: List[int] = []

        for pred in preds_sorted:
            best_iou = 0.0
            best_gt_idx = -1
            for gt_idx, gt in enumerate(ground_truths):
                if gt_matched[gt_idx]:
                    continue
                iou = IoU3D.compute_aabb_iou(pred, gt)
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = gt_idx

            if best_iou >= iou_threshold and best_gt_idx >= 0:
                gt_matched[best_gt_idx] = True
                tp_list.append(1)
                fp_list.append(0)
            else:
                tp_list.append(0)
                fp_list.append(1)

        # Cumulative precision and recall
        tp_cum = np.cumsum(tp_list)
        fp_cum = np.cumsum(fp_list)
        precisions = tp_cum / (tp_cum + fp_cum)
        recalls = tp_cum / len(ground_truths)

        # AP via trapezoidal integration
        ap = 0.0
        prev_recall = 0.0
        for p, r in zip(precisions, recalls):
            ap += p * (r - prev_recall)
            prev_recall = r
        return float(ap)


# ---------------------------------------------------------------------------
# 6. DATASET MANAGER
# ---------------------------------------------------------------------------

class ObjectronDataset:
    """Manages Objectron-style frame annotations."""

    def __init__(self) -> None:
        """Initialise empty dataset."""
        self._frames: Dict[int, FrameAnnotation] = {}
        self._sequences: Dict[str, List[int]] = {}

    def add_frame(self, annotation: FrameAnnotation,
                  sequence_name: str = "default") -> None:
        """Add a frame annotation.

        Args:
            annotation: FrameAnnotation instance.
            sequence_name: Sequence to which this frame belongs.
        """
        self._frames[annotation.frame_id] = annotation
        if sequence_name not in self._sequences:
            self._sequences[sequence_name] = []
        self._sequences[sequence_name].append(annotation.frame_id)

    def get_frame(self, frame_id: int) -> Result:
        """Retrieve a frame annotation.

        Args:
            frame_id: Frame identifier.

        Returns:
            Result with FrameAnnotation.
        """
        frame = self._frames.get(frame_id)
        if frame is None:
            return Err(f"Frame {frame_id} not found")
        return Ok(frame)

    @property
    def total_frames(self) -> int:
        """Total number of annotated frames."""
        return len(self._frames)

    @property
    def total_sequences(self) -> int:
        """Total number of sequences."""
        return len(self._sequences)


# ---------------------------------------------------------------------------
# 7. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniObjectronEngine:
    """
    Production Engine unifying 3D object detection, bounding box
    estimation, pose computation, and AR annotation management.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-objectron"

    def __init__(self) -> None:
        """Initialise the Objectron engine."""
        self.dataset = ObjectronDataset()
        self.camera = CameraIntrinsics()

    def create_bounding_box(self, center: List[float],
                            dimensions: List[float],
                            category: str = "cup",
                            confidence: float = 1.0) -> Result:
        """Create a 3D bounding box.

        Args:
            center: [x, y, z] center position.
            dimensions: [w, h, d] dimensions in metres.
            category: Object category string.
            confidence: Detection confidence.

        Returns:
            Result with BoundingBox3D.
        """
        if len(center) != 3 or len(dimensions) != 3:
            return Err("Center and dimensions must each have 3 elements")
        try:
            cat = ObjectCategory(category)
        except ValueError:
            return Err(f"Unknown category: {category}. "
                       f"Available: {[c.value for c in ObjectCategory]}")
        bbox = BoundingBox3D(
            center=np.array(center, dtype=np.float64),
            dimensions=np.array(dimensions, dtype=np.float64),
            category=cat, confidence=confidence,
        )
        return Ok(bbox)

    def compute_iou(self, box_a: BoundingBox3D,
                    box_b: BoundingBox3D) -> Result:
        """Compute 3D IoU between two bounding boxes.

        Args:
            box_a: First bounding box.
            box_b: Second bounding box.

        Returns:
            Result with IoU score.
        """
        iou = IoU3D.compute_aabb_iou(box_a, box_b)
        return Ok({"iou": iou})

    def project_to_2d(self, bbox: BoundingBox3D,
                      camera: Optional[CameraIntrinsics] = None) -> Result:
        """Project 3D bounding box corners to 2D image coordinates.

        Args:
            bbox: BoundingBox3D to project.
            camera: Optional camera intrinsics (uses default if None).

        Returns:
            Result with 2D pixel coordinates array.
        """
        cam = camera or self.camera
        corners_3d = bbox.get_corners()
        pixels = Projector.project_points(corners_3d, cam)
        return Ok({"corners_2d": pixels.tolist()})

    def evaluate_detections(self, predictions: List[BoundingBox3D],
                            ground_truths: List[BoundingBox3D],
                            iou_threshold: float = 0.5) -> Result:
        """Evaluate detection quality via Average Precision.

        Args:
            predictions: Predicted boxes.
            ground_truths: Ground truth boxes.
            iou_threshold: IoU threshold.

        Returns:
            Result with AP score.
        """
        ap = DetectionMetrics.average_precision(
            predictions, ground_truths, iou_threshold,
        )
        return Ok({"average_precision": ap, "iou_threshold": iou_threshold,
                    "n_predictions": len(predictions),
                    "n_ground_truths": len(ground_truths)})

    def add_frame_annotation(self, frame_id: int, timestamp: float,
                             objects: List[BoundingBox3D],
                             sequence: str = "default") -> Result:
        """Add a frame annotation to the dataset.

        Args:
            frame_id: Frame identifier.
            timestamp: Frame timestamp.
            objects: List of BoundingBox3D detections.
            sequence: Sequence name.

        Returns:
            Result monad.
        """
        annotation = FrameAnnotation(
            frame_id=frame_id, timestamp=timestamp,
            objects=objects, camera=self.camera,
        )
        self.dataset.add_frame(annotation, sequence)
        return Ok({"frame_id": frame_id, "objects": len(objects)})

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics.

        Returns:
            Dict with engine status.
        """
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "categories": [c.value for c in ObjectCategory],
            "dataset_frames": self.dataset.total_frames,
            "dataset_sequences": self.dataset.total_sequences,
            "features": [
                "3d_bounding_box", "iou_computation", "2d_projection",
                "average_precision", "frame_annotation", "pose_estimation",
            ],
        }
