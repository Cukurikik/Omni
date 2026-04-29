import torch
import torch.nn as nn

class CatalystTrainer:
    def __init__(self, model: nn.Module, optimizer: torch.optim.Optimizer):
        self.model = model
        self.optimizer = optimizer

    def train_step(self, x: torch.Tensor, y: torch.Tensor) -> float:
        try:
            self.optimizer.zero_grad()
            out = self.model(x)
            loss = nn.MSELoss()(out, y)
            loss.backward()
            self.optimizer.step()
            return float(loss.item())
        except Exception as e:
            raise RuntimeError(f"Catalyst training step failed: {e}")
