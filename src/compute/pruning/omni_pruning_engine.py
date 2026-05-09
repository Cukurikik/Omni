"""
omni_pruning_engine.py — Structured & Unstructured Pruning
Inspired by: Movement Pruning + Lottery Ticket Hypothesis
Layer: Compute / AI

Model compression via magnitude pruning, structured head pruning,
and iterative magnitude pruning with rewinding.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PruningConfig:
    target_sparsity: float = 0.5
    pruning_type: str = "unstructured"  # "unstructured", "structured", "movement"
    schedule: str = "cubic"             # "one_shot", "linear", "cubic"
    num_pruning_steps: int = 100
    warmup_steps: int = 10
    rewinding_step: Optional[int] = None  # Lottery ticket rewinding


class PruningMask:
    """Manages binary masks for weight pruning."""

    def __init__(self):
        self.masks: Dict[str, torch.Tensor] = {}

    def register(self, name: str, shape: torch.Size, device: torch.device):
        self.masks[name] = torch.ones(shape, dtype=torch.bool, device=device)

    def apply(self, name: str, weight: torch.Tensor) -> torch.Tensor:
        if name in self.masks:
            return weight * self.masks[name].float()
        return weight

    def update(self, name: str, mask: torch.Tensor):
        self.masks[name] = mask

    def sparsity(self, name: str) -> float:
        if name not in self.masks:
            return 0.0
        mask = self.masks[name]
        return 1.0 - mask.float().mean().item()

    def total_sparsity(self) -> float:
        total = 0
        pruned = 0
        for mask in self.masks.values():
            total += mask.numel()
            pruned += (~mask).sum().item()
        return pruned / max(1, total)

    def total_remaining(self) -> int:
        return sum(m.sum().item() for m in self.masks.values())


class MagnitudePruner:
    """Prune weights with smallest magnitude globally or per-layer."""

    @staticmethod
    def compute_threshold(weights: torch.Tensor, sparsity: float) -> float:
        """Compute magnitude threshold for target sparsity."""
        flat = weights.abs().flatten()
        k = int(flat.numel() * sparsity)
        if k <= 0:
            return 0.0
        threshold = flat.kthvalue(k).values.item()
        return threshold

    @staticmethod
    def create_mask(weights: torch.Tensor, sparsity: float) -> torch.Tensor:
        threshold = MagnitudePruner.compute_threshold(weights, sparsity)
        return weights.abs() > threshold


class StructuredPruner:
    """Prune entire attention heads or FFN neurons."""

    @staticmethod
    def score_heads(weight: torch.Tensor, num_heads: int) -> torch.Tensor:
        """Score attention heads by their L2 norm."""
        dim = weight.shape[0]
        head_dim = dim // num_heads
        scores = torch.zeros(num_heads, device=weight.device)
        for h in range(num_heads):
            head_weight = weight[h * head_dim:(h + 1) * head_dim]
            scores[h] = head_weight.norm(p=2)
        return scores

    @staticmethod
    def prune_heads(weight: torch.Tensor, num_heads: int,
                    num_to_prune: int) -> Tuple[torch.Tensor, List[int]]:
        """Remove lowest-scoring attention heads."""
        scores = StructuredPruner.score_heads(weight, num_heads)
        _, indices = scores.topk(num_to_prune, largest=False)
        pruned_indices = sorted(indices.tolist())

        dim = weight.shape[0]
        head_dim = dim // num_heads

        mask = torch.ones(dim, dtype=torch.bool, device=weight.device)
        for idx in pruned_indices:
            mask[idx * head_dim:(idx + 1) * head_dim] = False

        pruned_weight = weight[mask]
        return pruned_weight, pruned_indices

    @staticmethod
    def score_neurons(weight: torch.Tensor) -> torch.Tensor:
        """Score FFN neurons by L1 norm across fan-in."""
        return weight.abs().sum(dim=1)

    @staticmethod
    def prune_neurons(weight: torch.Tensor,
                      num_to_prune: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Remove lowest-scoring FFN neurons."""
        scores = StructuredPruner.score_neurons(weight)
        _, indices = scores.topk(num_to_prune, largest=False)
        mask = torch.ones(weight.shape[0], dtype=torch.bool, device=weight.device)
        mask[indices] = False
        return weight[mask], mask


class MovementPruner:
    """Prune based on gradient-weight movement during fine-tuning."""

    def __init__(self):
        self.movement_scores: Dict[str, torch.Tensor] = {}
        self._initial_weights: Dict[str, torch.Tensor] = {}

    def initialize(self, model: nn.Module):
        for name, param in model.named_parameters():
            if param.dim() >= 2:
                self._initial_weights[name] = param.data.clone()
                self.movement_scores[name] = torch.zeros_like(param.data)

    def update_scores(self, model: nn.Module):
        """Update movement scores based on weight changes and gradients."""
        for name, param in model.named_parameters():
            if name in self.movement_scores and param.grad is not None:
                # Movement = weight * gradient (positive = important)
                movement = param.data * param.grad
                self.movement_scores[name] += movement.abs()

    def create_mask(self, name: str, sparsity: float) -> torch.Tensor:
        if name not in self.movement_scores:
            return torch.ones(0)
        scores = self.movement_scores[name]
        threshold = scores.flatten().kthvalue(
            int(scores.numel() * sparsity)
        ).values.item()
        return scores > threshold


class SparsityScheduler:
    """Schedule sparsity level over training steps."""

    def __init__(self, config: PruningConfig):
        self.config = config

    def get_sparsity(self, step: int) -> float:
        """Compute current target sparsity for given step."""
        if step < self.config.warmup_steps:
            return 0.0

        progress = min(1.0, (step - self.config.warmup_steps) /
                       max(1, self.config.num_pruning_steps))

        if self.config.schedule == "one_shot":
            return self.config.target_sparsity if progress >= 1.0 else 0.0
        elif self.config.schedule == "linear":
            return self.config.target_sparsity * progress
        elif self.config.schedule == "cubic":
            return self.config.target_sparsity * (1 - (1 - progress) ** 3)
        else:
            return self.config.target_sparsity * progress


class OmniPruningEngine:
    """Production pruning engine with multiple strategies."""

    def __init__(self, model: nn.Module, config: PruningConfig):
        self.model = model
        self.config = config
        self.mask_manager = PruningMask()
        self.scheduler = SparsityScheduler(config)
        self.movement_pruner = MovementPruner() if config.pruning_type == "movement" else None
        self._step = 0

        # Initialize masks
        for name, param in model.named_parameters():
            if param.dim() >= 2:  # Only prune matrices
                self.mask_manager.register(name, param.shape, param.device)

        if self.movement_pruner:
            self.movement_pruner.initialize(model)

        # Save initial weights for lottery ticket rewinding
        if config.rewinding_step is not None:
            self._rewinding_state = None

    def step(self):
        """Execute one pruning step."""
        self._step += 1
        target_sparsity = self.scheduler.get_sparsity(self._step)

        if target_sparsity <= 0:
            return

        if self.config.pruning_type == "unstructured":
            self._prune_unstructured(target_sparsity)
        elif self.config.pruning_type == "structured":
            self._prune_structured(target_sparsity)
        elif self.config.pruning_type == "movement":
            if self.movement_pruner:
                self.movement_pruner.update_scores(self.model)
            self._prune_movement(target_sparsity)

        # Apply masks to weights
        self._apply_masks()

        # Save state for rewinding if at rewinding step
        if (self.config.rewinding_step is not None and
                self._step == self.config.rewinding_step):
            self._rewinding_state = {
                name: param.data.clone()
                for name, param in self.model.named_parameters()
            }

    def _prune_unstructured(self, target_sparsity: float):
        for name, param in self.model.named_parameters():
            if param.dim() >= 2:
                mask = MagnitudePruner.create_mask(param.data, target_sparsity)
                self.mask_manager.update(name, mask)

    def _prune_structured(self, target_sparsity: float):
        for name, param in self.model.named_parameters():
            if param.dim() >= 2:
                num_to_prune = int(param.shape[0] * target_sparsity)
                if num_to_prune > 0:
                    _, neuron_mask = StructuredPruner.prune_neurons(
                        param.data, num_to_prune
                    )
                    full_mask = neuron_mask.unsqueeze(1).expand_as(param)
                    self.mask_manager.update(name, full_mask)

    def _prune_movement(self, target_sparsity: float):
        if self.movement_pruner is None:
            return
        for name, param in self.model.named_parameters():
            if param.dim() >= 2:
                mask = self.movement_pruner.create_mask(name, target_sparsity)
                if mask.numel() > 0:
                    self.mask_manager.update(name, mask)

    def _apply_masks(self):
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                if name in self.mask_manager.masks:
                    param.data = self.mask_manager.apply(name, param.data)

    def report(self) -> Dict[str, float]:
        """Generate pruning report."""
        return {
            "step": self._step,
            "total_sparsity": self.mask_manager.total_sparsity(),
            "remaining_params": self.mask_manager.total_remaining(),
            "target_sparsity": self.scheduler.get_sparsity(self._step),
        }
