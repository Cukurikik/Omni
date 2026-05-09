"""
OMNI Transformer — EMA (Exponential Moving Average) for Training
Maintain shadow parameters for stable evaluation.
"""
import torch
import torch.nn as nn
from typing import Optional
import copy
import logging

logger = logging.getLogger(__name__)


class EMAModel:
    """Exponential Moving Average of model parameters."""
    def __init__(self, model: nn.Module, decay: float = 0.9999, device: Optional[torch.device] = None):
        self.decay = decay
        self.shadow = copy.deepcopy(model)
        self.shadow.eval()
        if device:
            self.shadow.to(device)
        self.num_updates = 0

    @torch.inference_mode()
    def update(self, model: nn.Module) -> None:
        self.num_updates += 1
        # Use warmup decay
        decay = min(self.decay, (1 + self.num_updates) / (10 + self.num_updates))
        for s_param, m_param in zip(self.shadow.parameters(), model.parameters()):
            s_param.data.mul_(decay).add_(m_param.data, alpha=1 - decay)

    def get_model(self) -> nn.Module:
        return self.shadow

    def state_dict(self):
        return {"shadow": self.shadow.state_dict(), "decay": self.decay, "num_updates": self.num_updates}

    def load_state_dict(self, state_dict):
        self.shadow.load_state_dict(state_dict["shadow"])
        self.decay = state_dict["decay"]
        self.num_updates = state_dict["num_updates"]
