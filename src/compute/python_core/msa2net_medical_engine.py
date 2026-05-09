import torch
import torch.nn as nn
from typing import Dict, Any

class MSA2NetEngine(nn.Module):
    """
    [BMVC 2024] MSA^2 Net: Multi-scale Adaptive Attention-guided Network for Medical Image Segmentation.
    """
    def __init__(self, in_channels: int = 1, num_classes: int = 2):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        # Adaptive Attention Block
        self.attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(64, 64 // 8, 1),
            nn.ReLU(),
            nn.Conv2d(64 // 8, 64, 1),
            nn.Sigmoid()
        )
        self.decoder = nn.Conv2d(64, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> Dict[str, Any]:
        try:
            feat = self.encoder(x)
            attn_weight = self.attention(feat)
            refined_feat = feat * attn_weight
            segmentation = self.decoder(refined_feat)
            
            return {"status": "success", "segmentation_map": segmentation}
        except Exception as e:
            return {"status": "error", "message": str(e)}
