# Omni VisionQA Multimodal Engine
from typing import List, Dict

def bounding_box_iou(box1: List[float], box2: List[float]) -> float:
    """Calculate Intersection over Union for two [x1, y1, x2, y2] bounding boxes."""
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
        
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    iou = intersection_area / max(float(box1_area + box2_area - intersection_area), 1e-8)
    return round(iou, 4)

def evaluate_vqa_accuracy(predictions: List[str], ground_truths: List[List[str]]) -> float:
    """Evaluate VQA accuracy where multiple ground truth variants exist per question."""
    if not predictions or not ground_truths or len(predictions) != len(ground_truths):
        return 0.0
        
    correct = 0
    for pred, truths in zip(predictions, ground_truths):
        pred_clean = pred.strip().lower()
        if any(pred_clean == t.strip().lower() for t in truths):
            correct += 1
            
    return round(correct / len(predictions), 4)
