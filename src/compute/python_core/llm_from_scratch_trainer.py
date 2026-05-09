import torch
import torch.nn as nn
from torch.optim import AdamW
from typing import Dict, Any

class LLMTrainer:
    def __init__(self, model: nn.Module, lr: float = 3e-4):
        self.model = model
        self.optimizer = AdamW(self.model.parameters(), lr=lr)

    def train_step(self, loss: torch.Tensor) -> Dict[str, Any]:
        try:
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            return {"status": "success", "loss": loss.item()}
        except Exception as e:
            return {"status": "error", "message": str(e)}
