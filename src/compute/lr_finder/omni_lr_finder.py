"""
omni_lr_finder.py — Learning Rate Range Finder
Inspired by: Cyclical LR paper + SoundStorm training
Layer: Compute / AI

Automatically finds optimal learning rate by running a short
training sweep with exponentially increasing LR.
"""

import torch
import torch.nn as nn
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class LRFinderResult:
    learning_rates: List[float] = field(default_factory=list)
    losses: List[float] = field(default_factory=list)
    smoothed_losses: List[float] = field(default_factory=list)
    best_lr: float = 0.0
    min_loss_lr: float = 0.0
    steepest_lr: float = 0.0

    def summary(self) -> str:
        return (
            f"LR Finder Results:\n"
            f"  Best LR (steepest gradient): {self.steepest_lr:.2e}\n"
            f"  Min Loss LR: {self.min_loss_lr:.2e}\n"
            f"  Suggested LR: {self.best_lr:.2e}"
        )


class OmniLRFinder:
    """Smith-style LR range test for finding optimal learning rate.

    Runs a short training sweep where LR increases exponentially
    from start_lr to end_lr, tracking loss at each step.
    """

    def __init__(self, model: nn.Module, optimizer: torch.optim.Optimizer,
                 criterion: nn.Module, device: torch.device):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self._initial_state = {
            "model": {k: v.clone() for k, v in model.state_dict().items()},
            "optimizer": optimizer.state_dict(),
        }

    def find(self, train_loader, start_lr: float = 1e-7,
             end_lr: float = 10.0, num_steps: int = 100,
             smooth_factor: float = 0.05,
             divergence_threshold: float = 4.0) -> LRFinderResult:
        """Run the LR range test."""
        result = LRFinderResult()
        self.model.train()

        lr_mult = (end_lr / start_lr) ** (1.0 / num_steps)
        current_lr = start_lr
        best_loss = float("inf")
        avg_loss = 0.0

        for pg in self.optimizer.param_groups:
            pg["lr"] = current_lr

        data_iter = iter(train_loader)
        step = 0

        while step < num_steps:
            try:
                batch = next(data_iter)
            except StopIteration:
                data_iter = iter(train_loader)
                batch = next(data_iter)

            if isinstance(batch, (list, tuple)):
                inputs = batch[0].to(self.device)
                targets = batch[1].to(self.device) if len(batch) > 1 else inputs
            else:
                inputs = batch.to(self.device)
                targets = inputs

            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            if isinstance(outputs, dict):
                loss = outputs.get("loss", self.criterion(outputs.get("logits", inputs), targets))
            else:
                loss = self.criterion(outputs, targets)

            # Smoothed loss
            avg_loss = smooth_factor * loss.item() + (1 - smooth_factor) * avg_loss if step > 0 else loss.item()
            smoothed = avg_loss / (1 - (1 - smooth_factor) ** (step + 1))

            if smoothed < best_loss:
                best_loss = smoothed

            # Stop if loss diverges
            if step > 10 and smoothed > best_loss * divergence_threshold:
                logger.info(f"Stopping LR finder: loss diverged at LR={current_lr:.2e}")
                break

            result.learning_rates.append(current_lr)
            result.losses.append(loss.item())
            result.smoothed_losses.append(smoothed)

            loss.backward()
            self.optimizer.step()

            current_lr *= lr_mult
            for pg in self.optimizer.param_groups:
                pg["lr"] = current_lr

            step += 1

        # Find optimal LR
        if len(result.smoothed_losses) > 2:
            min_idx = result.smoothed_losses.index(min(result.smoothed_losses))
            result.min_loss_lr = result.learning_rates[min_idx]

            # Steepest gradient point
            gradients = []
            for i in range(1, len(result.smoothed_losses)):
                grad = (result.smoothed_losses[i] - result.smoothed_losses[i-1]) / (
                    math.log10(result.learning_rates[i]) - math.log10(result.learning_rates[i-1]) + 1e-12
                )
                gradients.append(grad)

            if gradients:
                steepest_idx = gradients.index(min(gradients))
                result.steepest_lr = result.learning_rates[steepest_idx]

            # Suggested: one order of magnitude before min loss
            result.best_lr = result.min_loss_lr / 10.0

        # Restore initial model state
        self._restore()

        return result

    def _restore(self):
        """Restore model and optimizer to initial state."""
        self.model.load_state_dict(self._initial_state["model"])
        self.optimizer.load_state_dict(self._initial_state["optimizer"])
