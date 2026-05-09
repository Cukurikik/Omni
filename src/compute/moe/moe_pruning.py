"""
moe_pruning.py — Expert Pruning and Distillation
Layer: Compute / AI — Model Optimization

Methods to structurally prune an MoE model.
Can prune an N-expert MoE down to an M-expert MoE (M < N),
or collapse highly utilized experts into a dense baseline model
for deployment on constrained devices.
"""
import torch
import torch.nn as nn
from typing import List, Dict


class MoEPruner:
    """Handles structured pruning of MoE layers."""
    
    @staticmethod
    def identify_dead_experts(router_weights: nn.Linear, threshold: float = 1e-4) -> List[int]:
        """
        Identify experts whose routing weights (L2 norm) are near zero,
        meaning they are rarely or never selected.
        """
        # router_weights.weight: (num_experts, dim)
        norms = torch.norm(router_weights.weight, p=2, dim=1)
        dead_indices = (norms < threshold).nonzero(as_tuple=True)[0].tolist()
        return dead_indices

    @staticmethod
    def prune_experts(
        moe_layer: nn.Module, 
        experts_to_keep: List[int]
    ) -> nn.Module:
        """
        Creates a new MoE layer containing only the specified experts.
        """
        # Note: This expects a specific MoE module structure (customizable based on actual arch).
        # We assume `moe_layer.experts` is a ModuleList and `moe_layer.router.gate` is the linear layer.
        
        num_kept = len(experts_to_keep)
        old_num_experts = len(moe_layer.experts)
        dim = moe_layer.router.gate.weight.shape[1]
        
        # 1. Prune Router Gate
        new_gate = nn.Linear(dim, num_kept, bias=False)
        with torch.no_grad():
            new_gate.weight.copy_(moe_layer.router.gate.weight[experts_to_keep])
            
        # 2. Prune Experts
        new_experts = nn.ModuleList([moe_layer.experts[i] for i in experts_to_keep])
        
        # 3. Re-assemble (mocking the re-assignment)
        moe_layer.router.gate = new_gate
        moe_layer.router.num_experts = num_kept
        moe_layer.experts = new_experts
        
        return moe_layer

    @staticmethod
    def collapse_to_dense(
        moe_layer: nn.Module, 
        usage_stats: Dict[int, float]
    ) -> nn.Module:
        """
        Collapses the MoE into a single dense FeedForward layer
        by averaging the weights of the top N most used experts,
        weighted by their usage frequency.
        """
        dim = moe_layer.experts[0].w1.in_features
        hidden_dim = moe_layer.experts[0].w1.out_features
        
        # Create dense target
        dense_ffn = nn.Sequential(
            nn.Linear(dim, hidden_dim, bias=False),
            nn.SiLU(),
            nn.Linear(hidden_dim, dim, bias=False)
        )
        
        # Calculate weight mixing coefficients
        total_usage = sum(usage_stats.values())
        
        with torch.no_grad():
            dense_ffn[0].weight.zero_()
            dense_ffn[2].weight.zero_()
            
            for eid, usage in usage_stats.items():
                coeff = usage / total_usage
                expert = moe_layer.experts[eid]
                
                # W1: (hidden_dim, dim)
                dense_ffn[0].weight += expert.w1.weight * coeff
                # W2: (dim, hidden_dim)
                dense_ffn[2].weight += expert.w2.weight * coeff
                
        return dense_ffn
