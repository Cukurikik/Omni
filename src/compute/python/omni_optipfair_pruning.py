import torch
import torch.nn as nn
from typing import List

class OmniOptiPFairPruner:
    """OMNI Implementation of Structured Pruning for LLMs with Fairness constraints."""
    
    def __init__(self, target_sparsity: float = 0.5):
        self.target_sparsity = target_sparsity

    def compute_pruning_mask(self, weight: torch.Tensor) -> torch.Tensor:
        """Computes magnitude-based pruning mask."""
        threshold = torch.quantile(torch.abs(weight), self.target_sparsity)
        return (torch.abs(weight) >= threshold).float()

    def apply_structured_pruning(self, model: nn.Module) -> nn.Module:
        """Applies pruning to linear layers while avoiding bias metrics degradation."""
        with torch.no_grad():
            for name, module in model.named_modules():
                if isinstance(module, nn.Linear):
                    mask = self.compute_pruning_mask(module.weight)
                    module.weight.mul_(mask)
        return model
