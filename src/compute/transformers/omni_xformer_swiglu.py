"""
omni_xformer_swiglu.py — SwiGLU Activation Function
Layer: Compute / AI
Inspired by: facebookresearch/xformers (and LLaMA architecture)

Implements the SwiGLU (Swish-Gated Linear Unit) activation used in modern 
transformers. It replaces the standard ReLU/GELU in the feed-forward network,
providing smoother gradients and better empirical performance. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniSwiGLU(nn.Module):
    def __init__(self, in_features: int, hidden_features: int, out_features: int = None):
        """
        in_features: D_model
        hidden_features: Usually around 8/3 * D_model to maintain parameter parity
                         with standard MLPs (since we have 3 weight matrices).
        out_features: Defaults to in_features.
        """
        super().__init__()
        out_features = out_features or in_features
        
        # W1 and W3 are the "gates". We compute them together for efficiency.
        # W1 projects to the gate, W3 projects to the value.
        self.w1 = nn.Linear(in_features, hidden_features, bias=False)
        self.w3 = nn.Linear(in_features, hidden_features, bias=False)
        
        # W2 projects back to out_features
        self.w2 = nn.Linear(hidden_features, out_features, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, SeqLen, InFeatures)
        """
        # x1 = x * W1
        # x3 = x * W3
        x1 = self.w1(x)
        x3 = self.w3(x)
        
        # Swish(x) = x * sigmoid(beta * x), usually beta=1 so it's SiLU
        # SwiGLU = Swish(x1) * x3
        gated = F.silu(x1) * x3
        
        # Output = Gated * W2
        return self.w2(gated)

class OmniSwiGLUFFN(nn.Module):
    """
    A full Feed-Forward Network block using SwiGLU, ready to drop into a Transformer layer.
    """
    def __init__(self, d_model: int, hidden_dim: int):
        super().__init__()
        self.swiglu = OmniSwiGLU(
            in_features=d_model,
            hidden_features=hidden_dim,
            out_features=d_model
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.swiglu(x)
