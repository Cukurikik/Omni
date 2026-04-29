# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Ultralytics YOLOv3 (OMNI Zero-Mock Implementation)
# Implements Non-Maximum Suppression (NMS) bounding box filtering mathematically.

from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Result:
    value: Optional[List[Tuple[float, float, float, float, float]]] # Boxes + score
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[Tuple[float, float, float, float, float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class YOLOv3Engine:
    def _iou(self, box1: Tuple[float, float, float, float], box2: Tuple[float, float, float, float]) -> float:
        # box: (x1, y1, x2, y2)
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersect = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union = area1 + area2 - intersect
        return intersect / union if union > 0.0 else 0.0

    def non_max_suppression(self, boxes: List[Tuple[float, float, float, float, float, int]], iou_threshold: float, conf_threshold: float) -> Result:
        """
        boxes = [(x1, y1, x2, y2, confidence, class_id)]
        """
        if iou_threshold < 0.0 or iou_threshold > 1.0:
            return Result.err("IoU threshold must be between 0 and 1.")
            
        # Filter by confidence map
        filtered = [b for b in boxes if b[4] >= conf_threshold]
        # Sort by highest confidence
        filtered.sort(key=lambda x: x[4], reverse=True)
        
        kept = []
        while filtered:
             current = filtered.pop(0)
             kept.append(current)
             
             # Filter out overlapping bounded areas mathematically
             remaining = []
             for box in filtered:
                  # only suppress same class
                  if box[5] == current[5]:
                      iou = self._iou(current[:4], box[:4])
                      if iou < iou_threshold:
                          remaining.append(box)
                  else:
                      remaining.append(box)
             filtered = remaining
             
        return Result.ok(kept)
