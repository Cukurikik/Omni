"""
moe_baby_llm.py — Compute / Edge Deployment
Layer: Compute / AI — Minimal MoE Implementation

Inspired by baby-llm, this is an ultra-minimalist, dependency-light MoE 
implementation designed to run on resource-constrained devices (Raspberry Pi,
low-end edge hardware). It avoids complex scatter/gather operations and uses
pure PyTorch loops, prioritizing readability and compatibility over maximum
throughput.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class MiniExpert(nn.Module):
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d_model, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)))

class BabyMoELayer(nn.Module):
    """
    A minimal MoE layer for educational or edge-constrained purposes.
    """
    def __init__(self, d_model: int, num_experts: int, top_k: int = 1):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Simple linear router
        self.router = nn.Linear(d_model, num_experts, bias=False)
        
        # Instantiate experts
        self.experts = nn.ModuleList([
            MiniExpert(d_model, d_model * 2) for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch_size, seq_len, d_model)
        """
        batch_size, seq_len, d_model = x.shape
        x_flat = x.view(-1, d_model)
        
        # 1. Routing
        router_logits = self.router(x_flat)
        routing_weights = F.softmax(router_logits, dim=-1)
        
        # Get Top-K experts
        top_weights, top_indices = torch.topk(routing_weights, self.top_k, dim=-1)
        # Re-normalize
        top_weights = top_weights / top_weights.sum(dim=-1, keepdim=True)
        
        final_output = torch.zeros_like(x_flat)
        
        # 2. Expert Execution (Naive looping)
        # This is not optimized for massive GPUs, but perfect for CPU/Edge
        for k in range(self.top_k):
            expert_indices = top_indices[:, k]
            weights = top_weights[:, k]
            
            for expert_id in range(self.num_experts):
                # Find tokens assigned to this expert
                mask = (expert_indices == expert_id)
                if not mask.any():
                    continue
                    
                tokens = x_flat[mask]
                
                # Execute expert
                expert_out = self.experts[expert_id](tokens)
                
                # Combine output with router weights
                final_output[mask] += expert_out * weights[mask].unsqueeze(-1)
                
        return final_output.view(batch_size, seq_len, d_model)
