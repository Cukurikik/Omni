"""
omni_kan_linear.py — Kolmogorov-Arnold Network (KAN) Linear Layer
Layer: Compute / AI
Inspired by: Omid-Nejati/MedViTV2 (KAN-Integrated Transformers)

Implements a B-Spline based Kolmogorov-Arnold Network linear layer.
Replaces traditional fixed linear weights with learnable non-linear univariate 
functions on the edges, vastly improving expressivity for Medical ViTs.
Zero-mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniKANLinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, grid_size: int = 5, spline_order: int = 3):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.grid_size = grid_size
        self.spline_order = spline_order
        
        # Grid bounds
        grid = torch.linspace(-1, 1, steps=grid_size + 2 * spline_order + 1)
        self.register_buffer('grid', grid)
        
        # Base weight (like a standard linear layer for residual)
        self.base_weight = nn.Parameter(torch.Tensor(out_features, in_features))
        nn.init.kaiming_uniform_(self.base_weight, a=5**0.5)

        # Spline coefficients: (out_features, in_features, grid_size + spline_order)
        self.spline_coeff = nn.Parameter(torch.Tensor(out_features, in_features, grid_size + spline_order))
        nn.init.normal_(self.spline_coeff, std=0.1)

    def b_spline(self, x: torch.Tensor) -> torch.Tensor:
        """
        Evaluates the B-Spline basis functions for the input x.
        x: (Batch, InFeatures)
        Returns: (Batch, InFeatures, NumCoeffs)
        """
        # x shape: (B, In)
        # grid shape: (G)
        grid = self.grid.to(x.device)
        
        # Initialize order 0 splines (Indicator functions)
        # bases: (B, In, G - 1)
        x_expanded = x.unsqueeze(-1)
        bases = ((x_expanded >= grid[:-1]) & (x_expanded < grid[1:])).to(x.dtype)
        
        # Compute higher order splines via Cox-de Boor recursion
        for k in range(1, self.spline_order + 1):
            left_num = x_expanded - grid[:-k-1]
            left_den = grid[k:-1] - grid[:-k-1]
            left = (left_num / (left_den + 1e-8)) * bases[:, :, :-1]
            
            right_num = grid[k+1:] - x_expanded
            right_den = grid[k+1:] - grid[1:-k]
            right = (right_num / (right_den + 1e-8)) * bases[:, :, 1:]
            
            bases = left + right
            
        return bases

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, InFeatures) or (Batch, SeqLen, InFeatures)
        """
        original_shape = x.shape
        if x.dim() > 2:
            x = x.view(-1, self.in_features)

        # 1. Base Linear computation (Residual path)
        base_output = F.linear(F.silu(x), self.base_weight) # (B, Out)

        # 2. B-Spline computation
        # bases: (B, In, NumCoeffs)
        bases = self.b_spline(torch.tanh(x)) 
        
        # coeff: (Out, In, NumCoeffs)
        # We need to compute sum_{in} sum_{coeff} bases(b, in, c) * coeff(out, in, c)
        spline_output = torch.einsum('bic,oic->bo', bases, self.spline_coeff)

        # 3. Combine
        out = base_output + spline_output

        if len(original_shape) > 2:
            out = out.view(*original_shape[:-1], self.out_features)
            
        return out
