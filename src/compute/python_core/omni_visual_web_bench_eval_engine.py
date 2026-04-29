import uuid
from typing import Dict, Any, List
from dataclasses import dataclass, field
import numpy as np

# OMNI Monadic Type
@dataclass
class Result:
    is_ok: bool
    value: Any = None
    error: str = None

    @classmethod
    def Ok(cls, value: Any):
        return cls(is_ok=True, value=value)

    @classmethod
    def Err(cls, error: str):
        return cls(is_ok=False, error=error)

def ok(value: Any) -> Result:
    return Result.Ok(value)

def err(error: str) -> Result:
    return Result.Err(error)

@dataclass
class OmniVisualWebBenchEvalEngine:
    """
    OmniVisualWebBenchEvalEngine
    Domain: VisualWebBench
    Zero-mock engine computing grounding accuracy in spatial web interfaces. 
    It leverages Intersection over Union (IoU) of normalized bounding boxes 
    predicted by Multimodal LLMs versus truth DOM coordinates.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    iou_threshold: float = 0.5

    def _compute_iou(self, box1: np.ndarray, box2: np.ndarray) -> np.ndarray:
        """
        Computes intersection over union (IoU) between two arrays of bounding boxes.
        box specs: (x_min, y_min, x_max, y_max)
        """
        # (N, 1, 4) and (1, M, 4) -> broadcasting to (N, M, 4)
        box1 = box1[:, np.newaxis, :]
        box2 = box2[np.newaxis, :, :]

        inter_xmin = np.maximum(box1[..., 0], box2[..., 0])
        inter_ymin = np.maximum(box1[..., 1], box2[..., 1])
        inter_xmax = np.minimum(box1[..., 2], box2[..., 2])
        inter_ymax = np.minimum(box1[..., 3], box2[..., 3])

        inter_area = np.maximum(0.0, inter_xmax - inter_xmin) * np.maximum(0.0, inter_ymax - inter_ymin)

        area1 = (box1[..., 2] - box1[..., 0]) * (box1[..., 3] - box1[..., 1])
        area2 = (box2[..., 2] - box2[..., 0]) * (box2[..., 3] - box2[..., 1])

        union_area = area1 + area2 - inter_area
        iou = inter_area / np.maximum(union_area, 1e-9)

        return iou

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "predicted_boxes" not in payload or "ground_truth_boxes" not in payload:
                return err("Missing predicted_boxes or ground_truth_boxes.")
                
            pred_boxes = np.array(payload["predicted_boxes"], dtype=np.float32)
            gt_boxes = np.array(payload["ground_truth_boxes"], dtype=np.float32)

            if pred_boxes.ndim != 2 or pred_boxes.shape[1] != 4:
                return err("predicted_boxes must be shape (N, 4).")
            if gt_boxes.ndim != 2 or gt_boxes.shape[1] != 4:
                return err("ground_truth_boxes must be shape (M, 4).")

            # Validate box format constraints (e.g. x_min < x_max)
            if np.any(pred_boxes[:, 0] >= pred_boxes[:, 2]) or np.any(pred_boxes[:, 1] >= pred_boxes[:, 3]):
                return err("Degenerate predicted bounding boxes detected.")
                
            iou_matrix = self._compute_iou(pred_boxes, gt_boxes)
            
            # Bipartite matching or eager greedy matching. 
            # Eager matching along ground truth:
            max_iou_per_gt = np.max(iou_matrix, axis=0)
            
            hits = int(np.sum(max_iou_per_gt >= self.iou_threshold))
            total_targets = gt_boxes.shape[0]
            
            recall = hits / float(total_targets) if total_targets > 0 else 0.0

            return ok({
                "engine_id": self.engine_id,
                "iou_matrix": iou_matrix.tolist(),
                "grounding_recall": recall,
                "hits": hits,
                "total_targets": total_targets,
                "status": "Web Bench Grounding Scored"
            })

        except Exception as e:
            return err(f"VisualWebBench Evaluation failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniVisualWebBenchEvalEngine",
            "status": "Operational",
            "iou_threshold": self.iou_threshold
        }
