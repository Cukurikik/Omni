"""
omni_nms_filter.py — Non-Maximum Suppression (NMS)
Layer: Compute / AI

Implements a vectorized Non-Maximum Suppression algorithm to filter out 
overlapping bounding boxes in object detection pipelines (e.g., YOLO, R-CNN).
Zero-mock, utilizing standard IoU metrics.
"""

import torch

class OmniNMSFilter:
    @staticmethod
    def compute_iou(box1: torch.Tensor, box2: torch.Tensor) -> torch.Tensor:
        """
        Computes intersection over union (IoU) between two boxes.
        Boxes are assumed to be in (x1, y1, x2, y2) format.
        """
        x1 = torch.max(box1[0], box2[0])
        y1 = torch.max(box1[1], box2[1])
        x2 = torch.min(box1[2], box2[2])
        y2 = torch.min(box1[3], box2[3])

        intersection = torch.clamp(x2 - x1, min=0) * torch.clamp(y2 - y1, min=0)
        
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union = box1_area + box2_area - intersection
        
        return intersection / (union + 1e-6)

    @staticmethod
    def apply(bboxes: torch.Tensor, scores: torch.Tensor, iou_threshold: float = 0.5) -> torch.Tensor:
        """
        Applies Non-Maximum Suppression.
        
        bboxes: Tensor of shape (N, 4) in (x1, y1, x2, y2) format
        scores: Tensor of shape (N,) containing confidence scores
        iou_threshold: Float threshold for suppression
        
        Returns:
            Indices of the kept bounding boxes.
        """
        if bboxes.numel() == 0:
            return torch.empty((0,), dtype=torch.int64, device=bboxes.device)

        # Sort by scores in descending order
        sorted_indices = torch.argsort(scores, descending=True)
        keep = []

        while sorted_indices.numel() > 0:
            # Pick the box with the highest score
            current_idx = sorted_indices[0].item()
            keep.append(current_idx)

            if sorted_indices.numel() == 1:
                break

            # Compute IoU of the picked box with the rest
            current_box = bboxes[current_idx]
            rest_indices = sorted_indices[1:]
            rest_boxes = bboxes[rest_indices]

            # Vectorized IoU computation
            x1 = torch.max(current_box[0], rest_boxes[:, 0])
            y1 = torch.max(current_box[1], rest_boxes[:, 1])
            x2 = torch.min(current_box[2], rest_boxes[:, 2])
            y2 = torch.min(current_box[3], rest_boxes[:, 3])

            inter_area = torch.clamp(x2 - x1, min=0) * torch.clamp(y2 - y1, min=0)
            
            curr_area = (current_box[2] - current_box[0]) * (current_box[3] - current_box[1])
            rest_area = (rest_boxes[:, 2] - rest_boxes[:, 0]) * (rest_boxes[:, 3] - rest_boxes[:, 1])
            
            union_area = curr_area + rest_area - inter_area
            ious = inter_area / (union_area + 1e-6)

            # Keep only the boxes with IoU less than the threshold
            filtered_indices = ious <= iou_threshold
            sorted_indices = rest_indices[filtered_indices]

        return torch.tensor(keep, dtype=torch.int64, device=bboxes.device)
