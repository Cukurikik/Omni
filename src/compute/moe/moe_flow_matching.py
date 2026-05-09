"""
moe_flow_matching.py — Compute / Flow Matching MoE
Layer: Compute / AI — Continuous Transformations

Implements Flow Matching Mixture of Experts (FM-MoE), replacing conventional 
MLP experts with flow matching networks. Each expert learns a continuous 
transformation through an Ordinary Differential Equation (ODE), enabling 
more expressive feature mappings while maintaining sparse computational efficiency.
"""
import torch
import torch.nn as nn
from typing import Optional, Callable

class FlowMatchingExpert(nn.Module):
    """
    An expert that learns a continuous transformation via vector field integration
    instead of a discrete MLP projection.
    """
    def __init__(self, dim: int, hidden_dim: int, num_integration_steps: int = 5):
        super().__init__()
        self.dim = dim
        self.num_steps = num_integration_steps
        
        # Vector field parameterized by a neural network.
        # It takes both the current state x_t and the time t as inputs.
        self.vector_field = nn.Sequential(
            nn.Linear(dim + 1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Integrates the ODE forward in time from t=0 to t=1 using Euler method.
        """
        batch_size, seq_len, _ = x.shape
        dt = 1.0 / self.num_steps
        
        x_t = x
        for step in range(self.num_steps):
            t = torch.full((batch_size, seq_len, 1), step * dt, device=x.device, dtype=x.dtype)
            # Concatenate state and time
            state_time = torch.cat([x_t, t], dim=-1)
            
            # Predict the derivative dx/dt
            v_t = self.vector_field(state_time)
            
            # Euler integration step
            x_t = x_t + v_t * dt
            
        return x_t


class FMMoELayer(nn.Module):
    """
    Mixture of Flow Matching Experts layer.
    """
    def __init__(self, dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.dim = dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        self.router = nn.Linear(dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            FlowMatchingExpert(dim, dim * 2) for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, D = x.shape
        flat_x = x.view(-1, D)
        
        # Routing logic
        logits = self.router(flat_x)
        routing_weights = torch.softmax(logits, dim=-1)
        top_weights, top_indices = torch.topk(routing_weights, self.top_k, dim=-1)
        
        # Normalize weights
        top_weights = top_weights / top_weights.sum(dim=-1, keepdim=True)
        
        final_output = torch.zeros_like(flat_x)
        
        # Dispatch to Flow Matching Experts
        for k in range(self.top_k):
            indices_k = top_indices[:, k]
            weights_k = top_weights[:, k]
            
            for expert_id in range(self.num_experts):
                mask = (indices_k == expert_id)
                if not mask.any():
                    continue
                    
                expert_inputs = flat_x[mask].unsqueeze(1) # (N, 1, D)
                # Compute continuous transformation
                expert_outputs = self.experts[expert_id](expert_inputs).squeeze(1)
                
                final_output[mask] += expert_outputs * weights_k[mask].unsqueeze(-1)
                
        return final_output.view(B, S, D)
