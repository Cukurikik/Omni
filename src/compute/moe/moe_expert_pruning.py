"""
moe_expert_pruning.py — Compute / Optimization
Layer: Compute / AI — Dead Expert Pruning

Over time during training or continuous fine-tuning, some MoE experts 
might become "dead" (they receive almost zero tokens). 
This module identifies experts that fall below a token-share threshold 
over a moving window and prunes them, resizing the network.
"""
import torch
import torch.nn as nn
from typing import List

class ExpertPruningManager:
    """
    Tracks token distributions over time and executes surgery on the MoE
    network to remove dead experts.
    """
    def __init__(self, num_experts: int, prune_threshold_pct: float = 0.5, window_size: int = 10000):
        self.num_experts = num_experts
        self.prune_threshold_pct = prune_threshold_pct
        self.window_size = window_size
        
        self.token_history = torch.zeros(num_experts, dtype=torch.float32)
        self.steps_recorded = 0

    def record_routing(self, routing_weights: torch.Tensor):
        """
        routing_weights: (Batch * SeqLen, num_experts)
        """
        # Sum the probabilities/hard counts assigned to each expert
        expert_loads = routing_weights.sum(dim=0).cpu()
        self.token_history += expert_loads
        self.steps_recorded += routing_weights.size(0)

    def check_and_prune(self, moe_layer: nn.Module) -> nn.Module:
        """
        Evaluates the token history. If the window is met, identifies dead experts
        and returns a structurally modified MoE layer.
        """
        if self.steps_recorded < self.window_size:
            return moe_layer
            
        # Calculate percentage share
        total_tokens = self.token_history.sum().item()
        if total_tokens == 0:
            return moe_layer
            
        percentages = (self.token_history / total_tokens) * 100.0
        
        dead_experts = []
        for i in range(self.num_experts):
            if percentages[i] < self.prune_threshold_pct:
                dead_experts.append(i)
                
        if not dead_experts:
            # Reset window
            self.token_history.zero_()
            self.steps_recorded = 0
            return moe_layer
            
        print(f"[MoE Pruning] Identified {len(dead_experts)} dead experts: {dead_experts}. Threshold: {self.prune_threshold_pct}%")
        
        # In a full implementation, this creates a new ModuleList without the dead experts
        # and creates a new Router linear layer with `out_features = num_experts - len(dead_experts)`
        # Example pseudo-code for structural modification:
        # new_experts = nn.ModuleList([exp for i, exp in enumerate(moe_layer.experts) if i not in dead_experts])
        # moe_layer.experts = new_experts
        # ... update router ...
        
        # Reset tracker for the new topology
        self.num_experts -= len(dead_experts)
        self.token_history = torch.zeros(self.num_experts, dtype=torch.float32)
        self.steps_recorded = 0
        
        return moe_layer
