"""
OMNI Transformer — Activation Functions Collection
All production activation functions used in transformer architectures.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class QuickGELU(nn.Module):
    """Approximate GELU used in CLIP."""
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.sigmoid(1.702 * x)


class SwiGLU(nn.Module):
    """SwiGLU activation (LLaMA, PaLM)."""
    def __init__(self, dim: int, hidden_dim: int, bias: bool = False):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=bias)
        self.w2 = nn.Linear(hidden_dim, dim, bias=bias)
        self.w3 = nn.Linear(dim, hidden_dim, bias=bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w2(F.silu(self.w1(x)) * self.w3(x))


class GeGLU(nn.Module):
    """GeGLU activation (GLU variant with GELU)."""
    def __init__(self, dim: int, hidden_dim: int, bias: bool = False):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=bias)
        self.w2 = nn.Linear(hidden_dim, dim, bias=bias)
        self.w3 = nn.Linear(dim, hidden_dim, bias=bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w2(F.gelu(self.w1(x)) * self.w3(x))


class Mish(nn.Module):
    """Mish activation: x * tanh(softplus(x))."""
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.tanh(F.softplus(x))


class SquaredReLU(nn.Module):
    """Squared ReLU (Primer paper)."""
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.relu(x) ** 2


class StarReLU(nn.Module):
    """Star ReLU with learnable scale and bias."""
    def __init__(self):
        super().__init__()
        self.scale = nn.Parameter(torch.tensor(0.8944))
        self.bias = nn.Parameter(torch.tensor(-0.4472))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.scale * F.relu(x) ** 2 + self.bias


ACTIVATION_REGISTRY = {
    "relu": nn.ReLU,
    "gelu": nn.GELU,
    "silu": nn.SiLU,
    "quick_gelu": QuickGELU,
    "mish": Mish,
    "squared_relu": SquaredReLU,
    "star_relu": StarReLU,
    "tanh": nn.Tanh,
}


def get_activation(name: str) -> nn.Module:
    if name not in ACTIVATION_REGISTRY:
        raise ValueError(f"Unknown activation: {name}. Available: {list(ACTIVATION_REGISTRY.keys())}")
    return ACTIVATION_REGISTRY[name]()
