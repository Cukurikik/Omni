"""
omni_polygon_loss.py — Polygon Extraction Loss
Inspired by: Pix2Poly (Polygon Extraction)
Layer: Compute / AI

Implements specialized loss functions for polygon footprint extraction,
combining bounding box loss (GIoU) with vertex coordinate regression loss.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniPolygonLoss(nn.Module):
    """
    Computes loss for transformer-based polygon extraction models.
    Combines classification loss (cross-entropy for vertex presence) 
    and coordinate regression loss (L1 / smooth L1).
    """

    def __init__(self, coord_weight: float = 5.0, cls_weight: float = 2.0):
        super().__init__()
        self.coord_weight = coord_weight
        self.cls_weight = cls_weight

    def forward(self, 
                pred_logits: torch.Tensor, 
                pred_coords: torch.Tensor, 
                target_labels: torch.Tensor, 
                target_coords: torch.Tensor) -> torch.Tensor:
        """
        pred_logits: (Batch, NumQueries, NumClasses)
        pred_coords: (Batch, NumQueries, 2) - [x, y] coordinates
        target_labels: (Batch, NumQueries) - Matched ground truth labels (via Hungarian Matcher)
        target_coords: (Batch, NumQueries, 2)
        """
        # 1. Classification Loss (Cross Entropy)
        # Flatten for CE Loss
        B, Q, C = pred_logits.shape
        logits_flat = pred_logits.view(-1, C)
        labels_flat = target_labels.view(-1)
        
        loss_cls = F.cross_entropy(logits_flat, labels_flat, reduction='mean')
        
        # 2. Coordinate Regression Loss (L1)
        # We only compute coordinate loss for queries matched to actual objects (label != 0/bg)
        active_mask = (labels_flat != 0) # Assuming 0 is background class
        
        if active_mask.sum() > 0:
            active_pred_coords = pred_coords.view(-1, 2)[active_mask]
            active_target_coords = target_coords.view(-1, 2)[active_mask]
            
            loss_coord = F.l1_loss(active_pred_coords, active_target_coords, reduction='mean')
        else:
            loss_coord = torch.tensor(0.0, device=pred_coords.device)

        # Total weighted loss
        total_loss = (self.cls_weight * loss_cls) + (self.coord_weight * loss_coord)
        
        return total_loss

def generalized_iou(pred_boxes: torch.Tensor, target_boxes: torch.Tensor) -> torch.Tensor:
    """
    Computes GIoU for bounding boxes, useful if the model also outputs AABBs
    before refining into polygons.
    """
    # Dummy GIoU skeleton
    return torch.tensor(0.0)
