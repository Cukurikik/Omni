"""
moe_kolmogorov_arnold.py — Compute / MixKABRN
Layer: Compute / AI — Spline-based KAN Experts

Implements Mixture of Kolmogorov-Arnold Bit Retentive Networks (MixKABRN).
Replaces standard linear projection MLPs inside experts with Kolmogorov-Arnold 
Network (KAN) layers, which learn activation functions via B-splines on the edges
rather than fixed activations on nodes. 
"""
import torch
import torch.nn as nn
from typing import Optional

class SplineLinear(nn.Module):
    """
    1D B-spline mapping representing the continuous functions on edges in a KAN.
    """
    def __init__(self, in_features: int, out_features: int, grid_size: int = 5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.grid_size = grid_size
        
        # Grid parameters for spline interpolation
        self.grid = nn.Parameter(torch.linspace(-1, 1, grid_size + 1))
        # Control points for the splines
        self.coeffs = nn.Parameter(torch.randn(out_features, in_features, grid_size))
        nn.init.normal_(self.coeffs, std=0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq, in_features)
        Returns: (batch, seq, out_features)
        """
        # Simplified basis function representation for demonstration
        # A true KAN evaluates B-spline basis functions over the grid
        B, S, I = x.shape
        x_expanded = x.unsqueeze(-1) # (B, S, I, 1)
        
        # Distance to grid points
        dist = torch.exp(-((x_expanded - self.grid) ** 2)) # (B, S, I, G)
        
        # Multiply by coefficients and sum over input features and grid
        # dist: (B, S, I, G)
        # coeffs: (O, I, G)
        out = torch.einsum('bsig,oig->bso', dist, self.coeffs)
        return out


class KANExpert(nn.Module):
    """
    An expert using the Kolmogorov-Arnold representation theorem.
    Instead of Linear -> SiLU -> Linear, it uses parameterized spline functions.
    """
    def __init__(self, dim: int, hidden_dim: int, grid_size: int = 5):
        super().__init__()
        # KAN replaces standard weights with spline functions
        self.phi_1 = SplineLinear(dim, hidden_dim, grid_size)
        self.phi_2 = SplineLinear(hidden_dim, dim, grid_size)
        
        # Optional: Add base linear mapping for stability (KAN trick)
        self.base_w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.base_w2 = nn.Linear(hidden_dim, dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Evaluate spline functions
        spline_hidden = self.phi_1(x)
        # Add base linear transformation (SiLU provides base nonlinearity)
        base_hidden = nn.functional.silu(self.base_w1(x))
        
        hidden = spline_hidden + base_hidden
        
        spline_out = self.phi_2(hidden)
        base_out = self.base_w2(hidden)
        
        return spline_out + base_out

class MixKABRNLayer(nn.Module):
    """
    Mixture of Kolmogorov-Arnold Networks.
    """
    def __init__(self, dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.dim = dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        self.router = nn.Linear(dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            KANExpert(dim, dim * 2) for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, S, D = x.shape
        flat_x = x.view(-1, D)
        
        logits = self.router(flat_x)
        routing_weights = torch.softmax(logits, dim=-1)
        top_weights, top_indices = torch.topk(routing_weights, self.top_k, dim=-1)
        top_weights = top_weights / top_weights.sum(dim=-1, keepdim=True)
        
        final_output = torch.zeros_like(flat_x)
        
        for k in range(self.top_k):
            indices_k = top_indices[:, k]
            weights_k = top_weights[:, k]
            
            for expert_id in range(self.num_experts):
                mask = (indices_k == expert_id)
                if not mask.any(): continue
                    
                expert_inputs = flat_x[mask]
                expert_outputs = self.experts[expert_id](expert_inputs)
                final_output[mask] += expert_outputs * weights_k[mask].unsqueeze(-1)
                
        return final_output.view(B, S, D)
