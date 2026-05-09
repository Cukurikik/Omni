"""
OMNI Transformer — Learning Rate Finder
Find optimal LR using the Smith range test method.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class LRFinder:
    """Learning rate range test."""
    def __init__(self, model: nn.Module, optimizer):
        self.model = model
        self.optimizer = optimizer
        self.history = {"lr": [], "loss": []}
        self._state = None

    def find(self, dataloader: DataLoader, start_lr: float = 1e-7,
             end_lr: float = 10.0, num_steps: int = 100) -> Tuple[float, float]:
        self._state = {k: v.clone() for k, v in self.model.state_dict().items()}
        self.model.train()
        lr_mult = (end_lr / start_lr) ** (1 / num_steps)
        lr = start_lr
        for pg in self.optimizer.param_groups:
            pg["lr"] = lr
        best_loss = float("inf")
        avg_loss = 0.0
        batch_iter = iter(dataloader)

        for step in range(num_steps):
            try:
                batch = next(batch_iter)
            except StopIteration:
                batch_iter = iter(dataloader)
                batch = next(batch_iter)
            device = next(self.model.parameters()).device
            batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
            self.optimizer.zero_grad()
            outputs = self.model(**batch)
            loss = outputs["loss"] if isinstance(outputs, dict) else outputs
            avg_loss = 0.05 * loss.item() + 0.95 * avg_loss if step > 0 else loss.item()
            if avg_loss < best_loss:
                best_loss = avg_loss
            if step > 0 and avg_loss > 4 * best_loss:
                break
            self.history["lr"].append(lr)
            self.history["loss"].append(avg_loss)
            loss.backward()
            self.optimizer.step()
            lr *= lr_mult
            for pg in self.optimizer.param_groups:
                pg["lr"] = lr

        self.model.load_state_dict(self._state)
        min_idx = self.history["loss"].index(min(self.history["loss"]))
        suggested = self.history["lr"][max(0, min_idx - 5)]
        logger.info(f"LR Finder: suggested={suggested:.2e}")
        return suggested, self.history["lr"][min_idx]
