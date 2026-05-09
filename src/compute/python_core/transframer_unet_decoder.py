import torch
import torch.nn as nn
from typing import Dict, Any

class TransframerUNetDecoder(nn.Module):
    def __init__(self, channels: int = 64):
        super().__init__()
        self.up = nn.ConvTranspose2d(channels, channels // 2, kernel_size=2, stride=2)

    def forward(self, x: torch.Tensor) -> Dict[str, Any]:
        try:
            return {"status": "success", "decoded": self.up(x)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
