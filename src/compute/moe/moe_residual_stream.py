"""
moe_residual_stream.py — Advanced Residual Stream for MoE
Layer: Compute / AI — MoE Architecture

Implements advanced residual connection strategies for MoE blocks:
- DeepNorm-style initialization for deep MoE stability
- Pre-LN vs Post-LN variants
- Gated residual connections (Skip connections with learned gates)
- Shared residual bypass for un-routed tokens (Drop Tokens)
"""
import torch
import torch.nn as nn
import math
from typing import Optional, Tuple


class GatedResidual(nn.Module):
    """Learned gating for the residual connection (Highway networks)."""
    def __init__(self, dim: int):
        super().__init__()
        self.gate = nn.Linear(dim, dim)
        # Initialize gate to bias towards residual (identity)
        nn.init.constant_(self.gate.bias, 2.0)
        nn.init.zeros_(self.gate.weight)

    def forward(self, x: torch.Tensor, fx: torch.Tensor) -> torch.Tensor:
        g = torch.sigmoid(self.gate(x))
        return (1.0 - g) * x + g * fx


class MoEResidualStream(nn.Module):
    """Manages the residual stream wrapping an MoE layer."""
    def __init__(self, dim: int, num_layers: int, norm_type: str = "rmsnorm",
                 residual_type: str = "prenorm"):
        super().__init__()
        self.dim = dim
        self.num_layers = num_layers
        self.residual_type = residual_type

        if norm_type == "rmsnorm":
            self.norm = nn.RMSNorm(dim)
        else:
            self.norm = nn.LayerNorm(dim)

        if residual_type == "gated":
            self.gated_res = GatedResidual(dim)

        # DeepNorm scaling factors
        self.alpha = math.pow(2.0 * num_layers, 0.25)
        self.beta = math.pow(8.0 * num_layers, -0.25)

    def forward(self, x: torch.Tensor, moe_func) -> Tuple[torch.Tensor, dict]:
        """
        Args:
            x: Input tensor (B, S, D)
            moe_func: Callable representing the MoE expert layer
        Returns:
            Output tensor and dict of auxiliary outputs from MoE
        """
        if self.residual_type == "prenorm":
            # Standard Pre-LN
            normed_x = self.norm(x)
            moe_out = moe_func(normed_x)
            fx = moe_out["output"] if isinstance(moe_out, dict) else moe_out
            out = x + fx

        elif self.residual_type == "deepnorm":
            # DeepNorm for ultra-deep models (scaling residual and init)
            normed_x = self.norm(x)
            moe_out = moe_func(normed_x)
            fx = moe_out["output"] if isinstance(moe_out, dict) else moe_out
            out = x * self.alpha + fx

        elif self.residual_type == "gated":
            # Gated residual
            normed_x = self.norm(x)
            moe_out = moe_func(normed_x)
            fx = moe_out["output"] if isinstance(moe_out, dict) else moe_out
            out = self.gated_res(x, fx)

        elif self.residual_type == "postnorm":
            # Legacy Post-LN
            moe_out = moe_func(x)
            fx = moe_out["output"] if isinstance(moe_out, dict) else moe_out
            out = self.norm(x + fx)
            
        else:
            raise ValueError(f"Unknown residual type: {self.residual_type}")

        aux_dict = moe_out if isinstance(moe_out, dict) else {}
        return out, aux_dict

    def handle_dropped_tokens(
        self,
        x: torch.Tensor,
        fx: torch.Tensor,
        dropped_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Pass dropped tokens (tokens that exceeded expert capacity) directly
        through the residual stream without modification.
        """
        # dropped_mask: (B, S) boolean tensor
        out = x.clone()
        # Only add fx where not dropped
        valid = ~dropped_mask
        out[valid] = out[valid] + fx[valid]
        return out
