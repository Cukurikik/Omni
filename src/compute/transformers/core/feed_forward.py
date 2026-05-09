"""
OMNI Transformer Engine — Feed-Forward Network Module
Production-grade FFN with SwiGLU, GeGLU, and standard variants.
Learned from: LLaMA architecture, Mistral, Shekswess/tiny-reasoning-language-model
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class FFNActivation(Enum):
    RELU = auto()
    GELU = auto()
    SWIGLU = auto()
    GEGLU = auto()
    SILU = auto()


class PositionWiseFeedForward(nn.Module):
    """
    Position-wise Feed-Forward Network with multiple activation variants.

    Standard: FFN(x) = W2 · act(W1 · x + b1) + b2
    Gated:    FFN(x) = W2 · (act(W1 · x) ⊙ W3 · x) + b2

    Where ⊙ denotes element-wise multiplication (gating).
    """

    def __init__(
        self,
        embed_dim: int,
        ffn_dim: Optional[int] = None,
        activation: FFNActivation = FFNActivation.SWIGLU,
        dropout: float = 0.0,
        use_bias: bool = False,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.ffn_dim = ffn_dim or (4 * embed_dim)
        self.activation_type = activation
        self.is_gated = activation in (FFNActivation.SWIGLU, FFNActivation.GEGLU)

        if self.is_gated:
            self.gate_proj = nn.Linear(embed_dim, self.ffn_dim, bias=use_bias)
            self.up_proj = nn.Linear(embed_dim, self.ffn_dim, bias=use_bias)
        else:
            self.up_proj = nn.Linear(embed_dim, self.ffn_dim, bias=use_bias)

        self.down_proj = nn.Linear(self.ffn_dim, embed_dim, bias=use_bias)
        self.dropout = nn.Dropout(dropout) if dropout > 0.0 else nn.Identity()

        self._activation_fn = self._get_activation(activation)
        self._init_weights()

    @staticmethod
    def _get_activation(activation: FFNActivation):
        mapping = {
            FFNActivation.RELU: F.relu,
            FFNActivation.GELU: F.gelu,
            FFNActivation.SILU: F.silu,
            FFNActivation.SWIGLU: F.silu,
            FFNActivation.GEGLU: F.gelu,
        }
        return mapping[activation]

    def _init_weights(self) -> None:
        for name, module in self.named_modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_uniform_(module.weight, a=math.sqrt(5) if hasattr(math, 'sqrt') else 2.236)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, S, D) input tensor

        Returns:
            (B, S, D) output tensor
        """
        if self.is_gated:
            gate = self._activation_fn(self.gate_proj(x))
            up = self.up_proj(x)
            hidden = gate * up
        else:
            hidden = self._activation_fn(self.up_proj(x))

        hidden = self.dropout(hidden)
        output = self.down_proj(hidden)
        return output

    def extra_repr(self) -> str:
        return (
            f"embed_dim={self.embed_dim}, ffn_dim={self.ffn_dim}, "
            f"activation={self.activation_type.name}, gated={self.is_gated}"
        )


class MixtureOfExpertsFFN(nn.Module):
    """
    Sparse Mixture-of-Experts Feed-Forward Network.
    Routes each token to top-k experts out of N total experts.
    Learned from: Mixtral architecture, Switch Transformer.
    """

    def __init__(
        self,
        embed_dim: int,
        ffn_dim: int,
        num_experts: int = 8,
        top_k: int = 2,
        activation: FFNActivation = FFNActivation.SWIGLU,
        dropout: float = 0.0,
        use_bias: bool = False,
    ):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.embed_dim = embed_dim

        self.gate = nn.Linear(embed_dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            PositionWiseFeedForward(
                embed_dim=embed_dim,
                ffn_dim=ffn_dim,
                activation=activation,
                dropout=dropout,
                use_bias=use_bias,
            )
            for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, S, D)

        Returns:
            (B, S, D) - MoE output with load-balanced expert routing
        """
        B, S, D = x.shape
        x_flat = x.view(-1, D)  # (B*S, D)

        # Compute gating scores
        router_logits = self.gate(x_flat)  # (B*S, num_experts)
        router_probs = F.softmax(router_logits, dim=-1)

        # Select top-k experts
        topk_weights, topk_indices = torch.topk(router_probs, self.top_k, dim=-1)
        topk_weights = topk_weights / topk_weights.sum(dim=-1, keepdim=True)

        # Compute expert outputs
        output = torch.zeros_like(x_flat)
        for k in range(self.top_k):
            expert_indices = topk_indices[:, k]  # (B*S,)
            expert_weights = topk_weights[:, k].unsqueeze(-1)  # (B*S, 1)

            for expert_idx in range(self.num_experts):
                mask = expert_indices == expert_idx
                if mask.any():
                    expert_input = x_flat[mask]
                    expert_output = self.experts[expert_idx](expert_input.unsqueeze(0)).squeeze(0)
                    output[mask] += expert_weights[mask] * expert_output

        return output.view(B, S, D)

    def compute_load_balance_loss(self, x: torch.Tensor) -> torch.Tensor:
        """Auxiliary loss to encourage balanced expert utilization."""
        B, S, D = x.shape
        x_flat = x.view(-1, D)
        router_logits = self.gate(x_flat)
        router_probs = F.softmax(router_logits, dim=-1)

        # Fraction of tokens routed to each expert
        _, topk_indices = torch.topk(router_probs, self.top_k, dim=-1)
        expert_counts = torch.zeros(self.num_experts, device=x.device)
        for k in range(self.top_k):
            for i in range(self.num_experts):
                expert_counts[i] += (topk_indices[:, k] == i).float().sum()

        fraction = expert_counts / (B * S * self.top_k)
        avg_probs = router_probs.mean(dim=0)

        # Load balance loss: N * sum(fraction * avg_prob)
        loss = self.num_experts * (fraction * avg_probs).sum()
        return loss


import math  # noqa: E402 - needed for _init_weights
