import torch
import torch.nn as nn
from typing import Dict, Any

class HoiForecastEngine(nn.Module):
    """
    [CVPR 2022] HOI-Forecast: Joint hand motion and interaction hotspots prediction.
    """
    def __init__(self, feature_dim: int = 1024, seq_len: int = 16):
        super().__init__()
        self.seq_len = seq_len
        self.gru = nn.GRU(feature_dim, feature_dim // 2, batch_first=True)
        self.hand_predictor = nn.Linear(feature_dim // 2, 3 * 21) # 21 joints, 3D
        self.hotspot_predictor = nn.Sequential(
            nn.Linear(feature_dim // 2, 256),
            nn.ReLU(),
            nn.Linear(256, 1) # Hotspot probability
        )

    def forward(self, video_features: torch.Tensor) -> Dict[str, Any]:
        try:
            out, hidden = self.gru(video_features)
            last_state = out[:, -1, :]
            
            hand_motion = self.hand_predictor(last_state)
            hotspots = torch.sigmoid(self.hotspot_predictor(last_state))
            
            return {
                "status": "success",
                "hand_motion": hand_motion.view(-1, 21, 3),
                "interaction_hotspots": hotspots
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
