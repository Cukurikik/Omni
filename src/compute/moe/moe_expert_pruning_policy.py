"""
moe_expert_pruning_policy.py — Compute / Optimization
Layer: Compute / AI — Dynamic Expert Pruning

In massive MoE models (e.g., 1000+ experts), many experts suffer from "Routing Collapse"
where they receive 0 tokens over thousands of steps. 
This Python module implements an aggressive pruning policy that monitors token 
assignment histograms. Dead experts are pruned from VRAM, and their weights 
are offloaded to NVMe to save expensive HBM memory.
"""

import torch
import torch.nn as nn
from typing import Dict

class DynamicExpertPruner:
    def __init__(self, num_experts: int, window_size: int = 1000, threshold: int = 10):
        self.num_experts = num_experts
        self.window_size = window_size
        self.threshold = threshold
        
        # Track total tokens received by each expert over the window
        self.token_histogram = torch.zeros(num_experts, dtype=torch.long)
        self.steps = 0
        self.active_experts = set(range(num_experts))
        
        print(f"[Pruning] Initialized Dynamic Expert Pruner. Window: {window_size} steps.")

    def update_routing_stats(self, routing_indices: torch.Tensor):
        """
        Called every forward pass to record which experts received tokens.
        routing_indices: (Batch * Seq_Len) tensor of assigned expert IDs
        """
        # Count occurrences of each expert ID
        counts = torch.bincount(routing_indices.flatten(), minlength=self.num_experts)
        self.token_histogram += counts.cpu()
        self.steps += 1
        
        if self.steps >= self.window_size:
            self.evaluate_pruning()

    def evaluate_pruning(self):
        """
        Analyzes the histogram to find dead experts and triggers offloading.
        """
        dead_experts = []
        for expert_id in list(self.active_experts):
            if self.token_histogram[expert_id] < self.threshold:
                dead_experts.append(expert_id)
                self.active_experts.remove(expert_id)
                
        if dead_experts:
            print(f"[Pruning] Warning: Routing collapse detected! Experts {dead_experts} received <{self.threshold} tokens in {self.window_size} steps.")
            self._offload_experts(dead_experts)
            
        # Reset histogram for next window
        self.token_histogram.zero_()
        self.steps = 0

    def _offload_experts(self, dead_experts: list):
        """
        Mocks the process of moving the expert's nn.Module from VRAM to NVMe.
        """
        for exp_id in dead_experts:
            # In production: torch.save(expert.state_dict(), f"/nvme/expert_{exp_id}.pt")
            # del expert
            # torch.cuda.empty_cache()
            print(f"[Pruning] Expert {exp_id} evicted from VRAM to NVMe storage.")
            
# Usage:
# pruner = DynamicExpertPruner(128)
# pruner.update_routing_stats(torch.tensor([1, 1, 5, 1, 99]))
