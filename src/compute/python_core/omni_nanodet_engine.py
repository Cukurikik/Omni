"""
OMNI Nanodet Engine
===================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, Tuple

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniNanodetEngine:
    """
    omni-nanodet
    
    A zero-mock native engine simulating NanoDet's explicit Anchor-Free detection framework.
    Maps generalized Intersection over Union (GIoU) mathematically to evaluate
    box regressor offsets utilizing a topological center-based spatial mapping.
    """
    
    ENGINE_VERSION = "omni-s6-b8.1.0"
    
    def __init__(self, stride: int = 8):
        """Initialize OmniNanodetEngine."""
        self.stride = stride

    def compute_iou_and_giou(self, box_p: np.ndarray, box_g: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes standard IoU and Generalized IoU mathematically.
        Arrays should be of shape (N, 4) in format: [x1, y1, x2, y2].
        """
        # Intersection boxes
        inter_x1 = np.maximum(box_p[:, 0], box_g[:, 0])
        inter_y1 = np.maximum(box_p[:, 1], box_g[:, 1])
        inter_x2 = np.minimum(box_p[:, 2], box_g[:, 2])
        inter_y2 = np.minimum(box_p[:, 3], box_g[:, 3])
        
        inter_w = np.maximum(0, inter_x2 - inter_x1)
        inter_h = np.maximum(0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h
        
        # Areas
        area_p = np.maximum(0, box_p[:, 2] - box_p[:, 0]) * np.maximum(0, box_p[:, 3] - box_p[:, 1])
        area_g = np.maximum(0, box_g[:, 2] - box_g[:, 0]) * np.maximum(0, box_g[:, 3] - box_g[:, 1])
        
        union_area = area_p + area_g - inter_area + 1e-10
        iou = inter_area / union_area
        
        # Enclosing box (for GIoU)
        enclose_x1 = np.minimum(box_p[:, 0], box_g[:, 0])
        enclose_y1 = np.minimum(box_p[:, 1], box_g[:, 1])
        enclose_x2 = np.maximum(box_p[:, 2], box_g[:, 2])
        enclose_y2 = np.maximum(box_p[:, 3], box_g[:, 3])
        
        enclose_w = np.maximum(0, enclose_x2 - enclose_x1)
        enclose_h = np.maximum(0, enclose_y2 - enclose_y1)
        enclose_area = enclose_w * enclose_h + 1e-10
        
        giou = iou - (enclose_area - union_area) / enclose_area
        
        return iou, giou

    def distances_to_boxes(self, centers: np.ndarray, reg_distances: np.ndarray) -> np.ndarray:
        """
        Anchor-Free logic mapping FCOS offset arrays (l, t, r, b) to exact spatial boxes (x1, y1, x2, y2).
        centers: (N, 2) array of (cx, cy)
        reg_distances: (N, 4) array of (left, top, right, bottom)
        """
        cx = centers[:, 0]
        cy = centers[:, 1]
        
        l = reg_distances[:, 0]
        t = reg_distances[:, 1]
        r = reg_distances[:, 2]
        b = reg_distances[:, 3]
        
        x1 = cx - l
        y1 = cy - t
        x2 = cx + r
        y2 = cy + b
        
        # Stack to shape (N, 4)
        return np.column_stack((x1, y1, x2, y2))

    def compute_regression_loss(self, centers: np.ndarray, predicted_distances: np.ndarray, ground_truth_boxes: np.ndarray) -> Result:
        """
        Calculates loss over projected NanoDet outputs natively.
        Loss = 1 - GIoU
        """
        try:
            if centers.shape[0] != predicted_distances.shape[0] or centers.shape[0] != ground_truth_boxes.shape[0]:
                return Result(error="Mismatched tensor dimensions for box topologies.")
                
            # Decode predicted specific distances into concrete bounding ranges natively.
            predicted_boxes = self.distances_to_boxes(centers, predicted_distances)
            
            # Map algebraic intersections
            iou, giou = self.compute_iou_and_giou(predicted_boxes, ground_truth_boxes)
            
            # Nanodet GIoU Loss computation: Loss converges bounded exactly to GIoU bounds [-1, 1]
            loss_array = 1.0 - giou
            mean_loss = float(np.mean(loss_array))
            
            return Result(value={
                "mean_giou_loss": mean_loss,
                "mean_iou": float(np.mean(iou)),
                "predicted_boxes": predicted_boxes
            })
            
        except Exception as e:
            return Result(error=f"GIoU Loss Calculation Error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniNanodetEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "components": ["FCOS-Anchor-Free-Offsets", "Generalized-IoU-Algebra"]
        }
