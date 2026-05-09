"""
omni_qlora_linear.py — Low-Rank Adaptation (LoRA) Linear Layer
Layer: Compute / AI
Inspired by: euclaise/SlimTrainer

Implements parameter-efficient fine-tuning via LoRA.
Freezes the main base weight matrix and trains two low-rank matrices (A and B).
Zero-mock.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniLoRALinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, r: int = 8, lora_alpha: int = 16, lora_dropout: float = 0.05):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.r = r
        self.lora_alpha = lora_alpha
        
        # Scaling factor
        self.scaling = self.lora_alpha / self.r

        # Base Weight (Pre-trained, Frozen)
        self.base_weight = nn.Parameter(torch.Tensor(out_features, in_features), requires_grad=False)
        nn.init.kaiming_uniform_(self.base_weight, a=math.sqrt(5))

        # LoRA Matrices (Trainable)
        # A: (r, in_features)
        # B: (out_features, r)
        self.lora_A = nn.Parameter(torch.Tensor(r, in_features), requires_grad=True)
        self.lora_B = nn.Parameter(torch.Tensor(out_features, r), requires_grad=True)
        
        self.dropout = nn.Dropout(p=lora_dropout)

        self.reset_parameters()

    def reset_parameters(self):
        # Initialize A with Kaiming uniform
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        # Initialize B with zeros, so initial LoRA output is exactly 0 (no disruption)
        nn.init.zeros_(self.lora_B)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, ..., InFeatures)
        """
        # Base forward pass
        # Wx
        base_out = F.linear(x, self.base_weight)

        # LoRA forward pass
        # B * A * dropout(x) * scaling
        dropout_x = self.dropout(x)
        lora_A_out = F.linear(dropout_x, self.lora_A) # (Batch, ..., r)
        lora_out = F.linear(lora_A_out, self.lora_B)  # (Batch, ..., OutFeatures)
        
        return base_out + (lora_out * self.scaling)

    def merge_weights(self):
        """
        Bakes the LoRA weights permanently into the base weights for zero-overhead inference.
        """
        if self.lora_A.requires_grad:
            # W_new = W_base + (B @ A) * scaling
            with torch.no_grad():
                delta_w = (self.lora_B @ self.lora_A) * self.scaling
                self.base_weight.add_(delta_w)
                
            # Disable gradients and zero out LoRA matrices
            self.lora_A.requires_grad = False
            self.lora_B.requires_grad = False
