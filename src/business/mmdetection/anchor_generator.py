import torch
from typing import Tuple, Optional

# OMNI MMDETECTION: Anchor Generator
# Python logic to generate prior bounding boxes (anchors) across multiple feature map levels.
# Essential for Faster R-CNN, RetinaNet, etc.
# Source: open-mmlab/mmdetection

class AnchorGeneratorError(Exception):
    pass

class AnchorGenerator:
    """
    Generates regular grid of anchors given scales and ratios.
    """
    def __init__(self, base_size: int, scales: list, ratios: list):
        self.base_size = base_size
        self.scales = torch.tensor(scales, dtype=torch.float32)
        self.ratios = torch.tensor(ratios, dtype=torch.float32)
        self.base_anchors = self._generate_base_anchors()

    def _generate_base_anchors(self) -> torch.Tensor:
        """
        Generates base anchors centered at (0, 0) for one feature map location.
        """
        w = self.base_size
        h = self.base_size
        
        # Calculate widths and heights based on ratios
        h_ratios = torch.sqrt(self.ratios)
        w_ratios = 1 / h_ratios
        
        ws = (w * w_ratios[:, None] * self.scales[None, :]).view(-1)
        hs = (h * h_ratios[:, None] * self.scales[None, :]).view(-1)
        
        # Create anchors [x1, y1, x2, y2]
        # Centered at 0, 0 -> x1 = -ws/2, x2 = ws/2
        base_anchors = torch.stack([
            -ws / 2, -hs / 2, ws / 2, hs / 2
        ], dim=-1)
        
        return base_anchors

    def grid_anchors(self, featmap_size: Tuple[int, int], stride: int) -> Tuple[Optional[torch.Tensor], Optional[AnchorGeneratorError]]:
        """
        Generates anchors for the entire feature map grid.
        """
        try:
            feat_h, feat_w = featmap_size
            
            # Generate shifts (grid centers)
            shift_x = torch.arange(0, feat_w) * stride
            shift_y = torch.arange(0, feat_h) * stride
            
            shift_y, shift_x = torch.meshgrid(shift_y, shift_x, indexing='ij')
            shift_x = shift_x.reshape(-1)
            shift_y = shift_y.reshape(-1)
            
            # [x, y, x, y] to add to base anchors
            shifts = torch.stack([shift_x, shift_y, shift_x, shift_y], dim=-1)
            
            # Add shifts to base anchors
            # base_anchors: [N, 4], shifts: [K, 4] -> all_anchors: [K, N, 4]
            all_anchors = self.base_anchors[None, :, :] + shifts[:, None, :]
            all_anchors = all_anchors.view(-1, 4)
            
            return all_anchors, None
            
        except Exception as e:
            return None, AnchorGeneratorError(f"Anchor grid generation failed: {str(e)}")
