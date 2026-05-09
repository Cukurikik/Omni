import torch
import torch.nn as nn
from typing import Dict, Any

class TrajectoryPredictor(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.regressor = nn.Sequential(nn.Linear(input_dim, 64), nn.ReLU(), nn.Linear(64, 3))

    def forward(self, history: torch.Tensor) -> Dict[str, Any]:
        try:
            return {"status": "success", "trajectory": self.regressor(history)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
