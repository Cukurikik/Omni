"""
omni_yolo_head.py — YOLO Detection Head
Inspired by: TransCenter / Standard YOLO vision pipelines
Layer: Compute / AI

Provides the bounding box regression and classification head for use
with spatial transformer backbones.
"""

import torch
import torch.nn as nn
from typing import Tuple

class OmniYoloHead(nn.Module):
    """
    Detection head for bounding boxes and objectness.
    Typically attached after a CNN backbone or a Vision Transformer.
    """
    
    def __init__(self, in_channels: int, num_classes: int, num_anchors: int = 3):
        super().__init__()
        self.num_classes = num_classes
        self.num_anchors = num_anchors
        
        # Prediction consists of: 4 bbox coords + 1 objectness + num_classes
        out_channels = num_anchors * (5 + num_classes)
        
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, in_channels * 2, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(in_channels * 2),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(in_channels * 2, out_channels, kernel_size=1, padding=0)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, in_channels, Height, Width)
        Returns: (Batch, num_anchors, Height, Width, 5 + num_classes)
        """
        B, C, H, W = x.shape
        out = self.conv(x)
        
        # Reshape to separate anchors and prediction attributes
        out = out.view(B, self.num_anchors, 5 + self.num_classes, H, W)
        
        # Permute to (B, Anchors, H, W, Attributes)
        out = out.permute(0, 1, 3, 4, 2).contiguous()
        
        return out

    def decode_predictions(self, 
                           predictions: torch.Tensor, 
                           anchors: torch.Tensor, 
                           stride: int) -> torch.Tensor:
        """
        Converts raw network outputs (tx, ty, tw, th) to bounding box coordinates.
        """
        # Sigmoid applied to x, y, objectness, and classes
        preds = predictions.clone()
        preds[..., 0:2] = torch.sigmoid(preds[..., 0:2]) # tx, ty
        preds[..., 4:] = torch.sigmoid(preds[..., 4:])   # obj, classes
        
        B, A, H, W, _ = preds.shape
        
        # Create grid offsets
        grid_y, grid_x = torch.meshgrid([torch.arange(H), torch.arange(W)], indexing='ij')
        grid = torch.stack((grid_x, grid_y), dim=-1).to(preds.device).float()
        grid = grid.view(1, 1, H, W, 2)
        
        # Decode center x, y
        bx_by = (preds[..., 0:2] + grid) * stride
        
        # Decode width, height
        anchors_w_h = anchors.view(1, A, 1, 1, 2).to(preds.device)
        bw_bh = torch.exp(preds[..., 2:4]) * anchors_w_h
        
        # Combine back
        decoded = torch.cat((bx_by, bw_bh, preds[..., 4:]), dim=-1)
        return decoded
