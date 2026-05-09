"""
omni_bbox_utils.py — Bounding Box Utilities
Layer: Compute / AI

Provides high-speed utility functions for computer vision bounding boxes,
including Intersection over Union (IoU) and Non-Maximum Suppression (NMS).
"""

import torch

def box_iou(boxes1: torch.Tensor, boxes2: torch.Tensor) -> torch.Tensor:
    """
    Computes pairwise IoU between two sets of bounding boxes.
    Boxes should be in (x1, y1, x2, y2) format.
    boxes1: (N, 4)
    boxes2: (M, 4)
    Returns: (N, M) matrix of IoU scores
    """
    area1 = (boxes1[:, 2] - boxes1[:, 0]) * (boxes1[:, 3] - boxes1[:, 1])
    area2 = (boxes2[:, 2] - boxes2[:, 0]) * (boxes2[:, 3] - boxes2[:, 1])
    
    # Calculate intersections
    lt = torch.max(boxes1[:, None, :2], boxes2[:, :2])  # [N, M, 2]
    rb = torch.min(boxes1[:, None, 2:], boxes2[:, 2:])  # [N, M, 2]
    
    wh = (rb - lt).clamp(min=0)  # [N, M, 2]
    inter = wh[:, :, 0] * wh[:, :, 1]  # [N, M]
    
    # Union = area1 + area2 - intersection
    union = area1[:, None] + area2 - inter
    
    iou = inter / union.clamp(min=1e-6)
    return iou

def non_max_suppression(boxes: torch.Tensor, scores: torch.Tensor, iou_threshold: float = 0.5) -> torch.Tensor:
    """
    Performs Non-Maximum Suppression (NMS) on bounding boxes.
    Returns the indices of the boxes to keep.
    boxes: (N, 4)
    scores: (N,)
    """
    if boxes.numel() == 0:
        return torch.empty(0, dtype=torch.long, device=boxes.device)
        
    # Sort boxes by scores in descending order
    sorted_scores, order = scores.sort(descending=True)
    sorted_boxes = boxes[order]
    
    keep = []
    
    while order.numel() > 0:
        if order.numel() == 1:
            keep.append(order[0].item())
            break
            
        # Keep the one with the highest score
        i = order[0].item()
        keep.append(i)
        
        # Compute IoU of the kept box with the rest
        ious = box_iou(sorted_boxes[0:1], sorted_boxes[1:]).squeeze(0)
        
        # Keep boxes with IoU less than threshold
        mask = ious <= iou_threshold
        
        # Update order and boxes
        order = order[1:][mask]
        sorted_boxes = sorted_boxes[1:][mask]
        
    return torch.tensor(keep, dtype=torch.long, device=boxes.device)
