// OMNI YOLOv5 NMS Box Engine — Compute Layer (Python)
// Absorbing ultralytics/yolov5 geometric box reduction
// Non-Maximum Suppression exact IoU calculations

from typing import List, Dict, Any, Tuple

class YoloError(Exception):
    pass

class BoundingBox:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, score: float, class_id: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.score = score
        self.class_id = class_id
        
    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)

class OmniYolov5NmsBox:
    def __init__(self, iou_threshold: float = 0.45):
        self.iou_threshold = iou_threshold
        self.nms_evaluations = 0

    def compute_iou(self, boxA: BoundingBox, boxB: BoundingBox) -> float:
        # Determine intersection coordinates
        xA = max(boxA.x1, boxB.x1)
        yA = max(boxA.y1, boxB.y1)
        xB = min(boxA.x2, boxB.x2)
        yB = min(boxA.y2, boxB.y2)

        interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
        if interArea == 0.0:
            return 0.0

        boxAArea = boxA.area()
        boxBArea = boxB.area()

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def execute_nms(self, proposals: List[BoundingBox]) -> Tuple[bool, List[BoundingBox], str]:
        """
        Greedy NMS removing boxes with high geometric overlap for same class bounds.
        """
        try:
            self.nms_evaluations += 1
            if not proposals:
                return True, [], ""

            # Sort descending by confidence score
            sorted_boxes = sorted(proposals, key=lambda b: b.score, reverse=True)
            kept_boxes = []

            while sorted_boxes:
                current = sorted_boxes.pop(0)
                kept_boxes.append(current)
                
                next_boxes = []
                for b in sorted_boxes:
                    if b.class_id == current.class_id:
                        iou = self.compute_iou(current, b)
                        if iou < self.iou_threshold:
                            next_boxes.append(b)
                    else:
                        next_boxes.append(b)
                        
                sorted_boxes = next_boxes

            return True, kept_boxes, ""

        except Exception as e:
            return False, [], f"System NMS panic: {e}"

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniYolov5NmsBox",
            "evaluations_run": self.nms_evaluations,
            "status": "Operational"
        }
