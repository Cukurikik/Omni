# Omni ObjectDetection Dataset Validator (Python)
# Compute: Dataset validation for object detection.
# Ref: coderonion/awesome-object-detection-datasets
from typing import Dict, List

def validate_bbox(bbox: List[float]) -> bool:
    if len(bbox) != 4: return False
    x1, y1, x2, y2 = bbox
    return x2 > x1 and y2 > y1 and x1 >= 0 and y1 >= 0

def dataset_statistics(annotations: List[Dict]) -> Dict:
    valid = sum(1 for a in annotations if validate_bbox(a.get("bbox", [])))
    labels = {}
    for a in annotations:
        lbl = a.get("label", "unknown")
        labels[lbl] = labels.get(lbl, 0) + 1
    return {"total": len(annotations), "valid_bboxes": valid, "label_distribution": labels}
