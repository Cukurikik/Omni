"""
omni_yolo_anchor.py — YOLO Anchor Box Generator and IOU Calculator
Layer: Compute / Computer Vision
Inspired by: Darknet / YOLOv3/v4

Implements Intersection over Union (IoU) and Anchor Box clustering algorithms
essential for object detection neural networks. Calculates how tightly a predicted
bounding box fits the ground truth target. Zero mock.
"""

import torch
import numpy as np

def calculate_iou(box1: torch.Tensor, box2: torch.Tensor) -> torch.Tensor:
    """
    Calculates Intersection over Union (IoU) between two bounding boxes.
    Assumes box format: (x_center, y_center, width, height)
    """
    # Convert from (xc, yc, w, h) to (x1, y1, x2, y2)
    b1_x1 = box1[..., 0] - box1[..., 2] / 2
    b1_y1 = box1[..., 1] - box1[..., 3] / 2
    b1_x2 = box1[..., 0] + box1[..., 2] / 2
    b1_y2 = box1[..., 1] + box1[..., 3] / 2

    b2_x1 = box2[..., 0] - box2[..., 2] / 2
    b2_y1 = box2[..., 1] - box2[..., 3] / 2
    b2_x2 = box2[..., 0] + box2[..., 2] / 2
    b2_y2 = box2[..., 1] + box2[..., 3] / 2

    # Intersection boundaries
    inter_x1 = torch.max(b1_x1, b2_x1)
    inter_y1 = torch.max(b1_y1, b2_y1)
    inter_x2 = torch.min(b1_x2, b2_x2)
    inter_y2 = torch.min(b1_y2, b2_y2)

    # Intersection Area
    inter_area = torch.clamp(inter_x2 - inter_x1, min=0) * torch.clamp(inter_y2 - inter_y1, min=0)

    # Union Area
    b1_area = (b1_x2 - b1_x1) * (b1_y2 - b1_y1)
    b2_area = (b2_x2 - b2_x1) * (b2_y2 - b2_y1)
    union_area = b1_area + b2_area - inter_area + 1e-16 # epsilon to prevent div/0

    return inter_area / union_area

def k_means_anchors(dataset_boxes: np.ndarray, num_anchors: int = 9, epochs: int = 100) -> np.ndarray:
    """
    Runs K-Means clustering on the dataset's ground truth bounding boxes to 
    generate optimal prior anchor boxes. Uses (1 - IoU) as the distance metric.
    
    dataset_boxes: numpy array of shape (N, 2) where col 0 is Width, col 1 is Height.
    """
    N = dataset_boxes.shape[0]
    
    # Initialize cluster centroids randomly from existing boxes
    indices = np.random.choice(N, num_anchors, replace=False)
    clusters = dataset_boxes[indices].copy()
    
    prev_assignments = np.zeros(N)
    
    for epoch in range(epochs):
        # Calculate distance (1 - IoU) from each box to each cluster center
        # Since we only care about w and h, assume xc=0, yc=0
        
        # Expand dims to compute all pairs
        # dataset_boxes: (N, 1, 2)
        # clusters: (1, K, 2)
        w_d = dataset_boxes[:, 0:1]
        h_d = dataset_boxes[:, 1:2]
        
        w_c = clusters[np.newaxis, :, 0]
        h_c = clusters[np.newaxis, :, 1]
        
        inter_area = np.minimum(w_d, w_c) * np.minimum(h_d, h_c)
        union_area = (w_d * h_d) + (w_c * h_c) - inter_area
        
        iou = inter_area / (union_area + 1e-16)
        distances = 1.0 - iou
        
        # Assign box to closest cluster
        assignments = np.argmin(distances, axis=1)
        
        if (assignments == prev_assignments).all():
            break # Converged
            
        prev_assignments = assignments.copy()
        
        # Update clusters
        for i in range(num_anchors):
            assigned_boxes = dataset_boxes[assignments == i]
            if len(assigned_boxes) > 0:
                clusters[i] = np.median(assigned_boxes, axis=0) # Median is more robust than mean
                
    # Sort by area
    areas = clusters[:, 0] * clusters[:, 1]
    clusters = clusters[np.argsort(areas)]
    
    return clusters
