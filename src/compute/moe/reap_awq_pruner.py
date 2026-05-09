"""
reap_awq_pruner.py — Compute / Optimization
Layer: Compute / AI — Expert Pruning & Quantization

Inspired by research-test-Qwen3-Coder-Next-REAP-AWQ.
Implements Relative Expert Activation Pruning (REAP) to permanently excise 
experts that rarely activate on the target distribution, combined with 
Activation-aware Weight Quantization (AWQ) calibration stubs.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple

class REAPExpertPruner:
    """
    Tracks expert activation frequencies over a calibration dataset 
    and prunes the least active experts to compress the MoE model.
    """
    def __init__(self, num_experts: int, prune_ratio: float = 0.2):
        self.num_experts = num_experts
        self.prune_ratio = prune_ratio
        
        # Accumulate activation counts for each expert
        self.activation_counts = torch.zeros(num_experts, dtype=torch.long)
        self.is_calibrated = False

    def update_activations(self, routing_indices: torch.Tensor):
        """
        routing_indices: Tensor of shape (..., top_k) containing selected expert IDs.
        Call this during the forward pass over the calibration dataset.
        """
        flat_indices = routing_indices.view(-1)
        # Bincount efficiently counts occurrences of each integer in the tensor
        counts = torch.bincount(flat_indices, minlength=self.num_experts).cpu()
        self.activation_counts += counts

    def compute_pruning_mask(self) -> torch.Tensor:
        """
        Determines which experts to keep and which to prune.
        Returns a boolean mask where True means KEEP.
        """
        self.is_calibrated = True
        num_to_prune = int(self.num_experts * self.prune_ratio)
        num_to_keep = self.num_experts - num_to_prune
        
        # Get the indices of the experts with the highest activation counts
        _, top_indices = torch.topk(self.activation_counts, num_to_keep)
        
        mask = torch.zeros(self.num_experts, dtype=torch.bool)
        mask[top_indices] = True
        
        print(f"[REAP] Pruning complete. Keeping {num_to_keep}/{self.num_experts} experts.")
        print(f"[REAP] Dropped experts: {torch.nonzero(~mask).squeeze(-1).tolist()}")
        
        return mask

class AWQCalibrationHook:
    """
    Stub for Activation-aware Weight Quantization.
    Records the average absolute activation magnitudes of the inputs to each expert,
    which is necessary to identify salient weight channels that should be protected
    during 4-bit/8-bit quantization.
    """
    def __init__(self, hidden_dim: int):
        self.activation_magnitudes = torch.zeros(hidden_dim)
        self.num_batches = 0

    def __call__(self, module: nn.Module, inputs: Tuple[torch.Tensor], output: torch.Tensor):
        # inputs[0] shape: (tokens, hidden_dim)
        x = inputs[0].detach().abs()
        mean_magnitude = x.mean(dim=0).cpu()
        
        # Moving average
        self.activation_magnitudes = (self.activation_magnitudes * self.num_batches + mean_magnitude) / (self.num_batches + 1)
        self.num_batches += 1
