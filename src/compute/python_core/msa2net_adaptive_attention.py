import torch
import torch.nn as nn
from typing import Dict, Any

class AdaptiveAttention(nn.Module):
    def __init__(self, in_channels: int):
        super().__init__()
        self.spatial_attn = nn.Conv2d(in_channels, 1, kernel_size=1)

    def forward(self, x: torch.Tensor) -> Dict[str, Any]:
        try:
            mask = torch.sigmoid(self.spatial_attn(x))
            return {"status": "success", "attended_features": x * mask}
        except Exception as e:
            return {"status": "error", "message": str(e)}
