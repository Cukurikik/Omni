"""
omni_image_cropper.py — Dynamic Image Cropping
Inspired by: COCO-LM and TransCenter
Layer: Compute / AI

Provides dynamic, attention-driven image cropping to focus computational
resources on high-information regions of an image before feeding to ViTs.
"""

import torch
import torch.nn.functional as F
from typing import Tuple

class OmniAttentionCropper:
    """
    Given a rough saliency map or preliminary attention map, this module
    generates bounding box coordinates for a high-resolution crop.
    """

    def __init__(self, crop_size: Tuple[int, int] = (224, 224), threshold: float = 0.5):
        self.crop_h, self.crop_w = crop_size
        self.threshold = threshold

    def get_crop_coordinates(self, saliency_map: torch.Tensor) -> torch.Tensor:
        """
        saliency_map: (Batch, 1, H, W) normalized between 0 and 1
        Returns bounding boxes: (Batch, 4) as [y1, x1, y2, x2]
        """
        B, _, H, W = saliency_map.shape
        boxes = []
        
        for b in range(B):
            # Threshold the saliency map to find regions of interest
            mask = saliency_map[b, 0] > self.threshold
            
            # Find indices where mask is True
            coords = torch.nonzero(mask)
            
            if len(coords) == 0:
                # Fallback to center crop
                y1 = max(0, (H - self.crop_h) // 2)
                x1 = max(0, (W - self.crop_w) // 2)
                boxes.append([y1, x1, y1 + self.crop_h, x1 + self.crop_w])
                continue
                
            # Get min/max bounds
            y_min, x_min = coords.min(dim=0)[0]
            y_max, x_max = coords.max(dim=0)[0]
            
            # Calculate center of mass
            center_y = (y_min + y_max) // 2
            center_x = (x_min + x_max) // 2
            
            # Extract crop window centered at center of mass
            y1 = max(0, center_y - self.crop_h // 2)
            x1 = max(0, center_x - self.crop_w // 2)
            
            y2 = min(H, y1 + self.crop_h)
            x2 = min(W, x1 + self.crop_w)
            
            # Adjust if bounds hit the edge
            if (y2 - y1) < self.crop_h:
                if y1 == 0: y2 = min(H, self.crop_h)
                else: y1 = max(0, H - self.crop_h)
                
            if (x2 - x1) < self.crop_w:
                if x1 == 0: x2 = min(W, self.crop_w)
                else: x1 = max(0, W - self.crop_w)
                
            boxes.append([y1.item(), x1.item(), y2.item(), x2.item()])
            
        return torch.tensor(boxes, device=saliency_map.device)

    def crop_images(self, images: torch.Tensor, boxes: torch.Tensor) -> torch.Tensor:
        """
        images: (Batch, Channels, H, W)
        boxes: (Batch, 4)
        """
        B, C, H, W = images.shape
        cropped = torch.zeros(B, C, self.crop_h, self.crop_w, device=images.device)
        
        for b in range(B):
            y1, x1, y2, x2 = boxes[b].int()
            cropped[b] = images[b, :, y1:y2, x1:x2]
            
        return cropped
