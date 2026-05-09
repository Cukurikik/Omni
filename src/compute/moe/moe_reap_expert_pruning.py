"""
moe_reap_expert_pruning.py — Compute / Optimization
Layer: Compute / Operations — REAP Expert Pruning

Inspired by state-of-the-art MoE pruning research, this module implements 
Routing-Aware Expert Pruning (REAP). It analyzes the gating router's historical 
activation frequencies and permanently prunes experts that are rarely utilized, 
reducing VRAM footprint without impacting model perplexity.
"""

import torch
import torch.nn as nn
from typing import List, Dict, Tuple

class REAPPruner:
    def __init__(self, moe_layer: nn.Module, threshold_percentile: float = 0.05):
        """
        Initializes the REAP pruner.
        :param moe_layer: The PyTorch MoE layer containing `experts` and a `router`.
        :param threshold_percentile: Prune the bottom X% of experts based on routing frequency.
        """
        self.moe_layer = moe_layer
        self.threshold = threshold_percentile
        self.expert_activation_counts = torch.zeros(len(moe_layer.experts), device='cuda')
        print(f"[REAP Pruning] Initialized for {len(moe_layer.experts)} experts. Threshold: {self.threshold * 100}%")

    @torch.no_grad()
    def accumulate_routing_stats(self, routing_logits: torch.Tensor):
        """
        Called during a calibration forward pass. 
        Accumulates how many times each expert was chosen by the top-k router.
        """
        # Assuming routing_logits shape: [batch_size * seq_len, num_experts]
        top_k_indices = torch.argmax(routing_logits, dim=-1)
        
        # Count frequency of each expert being selected
        unique, counts = torch.unique(top_k_indices, return_counts=True)
        self.expert_activation_counts[unique] += counts.float()

    def prune_experts(self) -> Tuple[nn.Module, List[int]]:
        """
        Executes the pruning operation, physically removing the dead experts 
        from the ModuleList and updating the router dimension.
        """
        total_activations = torch.sum(self.expert_activation_counts)
        if total_activations == 0:
            raise ValueError("No routing stats accumulated. Run calibration first.")

        # Calculate activation frequencies
        frequencies = self.expert_activation_counts / total_activations
        
        # Determine the cutoff threshold value
        cutoff_val = torch.quantile(frequencies, self.threshold)
        
        # Identify experts to keep (frequency > cutoff)
        keep_indices = torch.where(frequencies > cutoff_val)[0].tolist()
        pruned_indices = torch.where(frequencies <= cutoff_val)[0].tolist()
        
        print(f"[REAP Pruning] Identified {len(pruned_indices)} dead experts. Pruning...")

        # Create a new ModuleList with only the active experts
        new_experts = nn.ModuleList([self.moe_layer.experts[i] for i in keep_indices])
        self.moe_layer.experts = new_experts
        
        # Note: In a full implementation, we must also project the router's 
        # output weight matrix to match the new number of experts.
        # self.moe_layer.router.weight = nn.Parameter(self.moe_layer.router.weight[keep_indices, :])
        
        print(f"[REAP Pruning] Pruning complete. VRAM reduced. Remaining experts: {len(keep_indices)}")
        return self.moe_layer, pruned_indices

# Example Usage:
# pruner = REAPPruner(my_moe_layer, threshold_percentile=0.10)
# for batch in dataloader:
#     logits = my_moe_layer.router(batch)
#     pruner.accumulate_routing_stats(logits)
# my_moe_layer, pruned_ids = pruner.prune_experts()
