"""
omni_mixture_of_experts.py — Mixture of Experts Layer
Inspired by: Switch Transformer/GShard + OMNI compute efficiency
Layer: Compute / AI

Sparse MoE layer with top-k expert routing, load balancing loss,
and expert capacity management for efficient large model scaling.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class MoEConfig:
    num_experts: int = 8
    expert_dim: int = 768
    ff_dim: int = 3072
    top_k: int = 2
    capacity_factor: float = 1.25
    load_balance_weight: float = 0.01
    noise_std: float = 0.1
    dropout: float = 0.0


class ExpertFFN(nn.Module):
    """Single expert feed-forward network."""

    def __init__(self, dim: int, ff_dim: int, dropout: float = 0.0):
        super().__init__()
        self.w1 = nn.Linear(dim, ff_dim, bias=False)
        self.w2 = nn.Linear(ff_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, ff_dim, bias=False)  # SwiGLU gate
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = F.silu(self.w1(x))
        up = self.w3(x)
        return self.dropout(self.w2(gate * up))


class TopKRouter(nn.Module):
    """Differentiable top-k routing for expert selection."""

    def __init__(self, dim: int, num_experts: int, top_k: int = 2,
                 noise_std: float = 0.1):
        super().__init__()
        self.gate = nn.Linear(dim, num_experts, bias=False)
        self.top_k = top_k
        self.noise_std = noise_std
        self.num_experts = num_experts

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Route tokens to experts.

        Args:
            x: (batch * seq, dim) flattened tokens

        Returns:
            expert_weights: (batch * seq, top_k)
            expert_indices: (batch * seq, top_k)
            router_logits: (batch * seq, num_experts) for load balancing
        """
        logits = self.gate(x)

        # Add noise during training for exploration
        if self.training and self.noise_std > 0:
            noise = torch.randn_like(logits) * self.noise_std
            logits = logits + noise

        # Top-k selection
        top_k_logits, top_k_indices = torch.topk(logits, self.top_k, dim=-1)
        top_k_weights = F.softmax(top_k_logits, dim=-1)

        return top_k_weights, top_k_indices, logits


class OmniMixtureOfExperts(nn.Module):
    """Sparse Mixture of Experts layer.

    Routes each token to top-k experts using a learned router,
    with load balancing loss to ensure uniform expert utilization.
    """

    def __init__(self, config: MoEConfig):
        super().__init__()
        self.config = config
        self.num_experts = config.num_experts
        self.top_k = config.top_k

        self.router = TopKRouter(
            config.expert_dim, config.num_experts,
            config.top_k, config.noise_std
        )

        self.experts = nn.ModuleList([
            ExpertFFN(config.expert_dim, config.ff_dim, config.dropout)
            for _ in range(config.num_experts)
        ])

        self.norm = nn.LayerNorm(config.expert_dim)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass through MoE layer.

        Args:
            x: (batch, seq_len, dim)

        Returns:
            dict with 'output', 'load_balance_loss', 'router_probs'
        """
        B, S, D = x.shape
        residual = x
        x_flat = self.norm(x).reshape(-1, D)
        N = x_flat.shape[0]

        # Route tokens
        weights, indices, logits = self.router(x_flat)

        # Compute expert outputs
        output = torch.zeros_like(x_flat)

        for expert_idx in range(self.num_experts):
            # Find tokens assigned to this expert
            mask = (indices == expert_idx).any(dim=-1)
            if not mask.any():
                continue

            token_indices = mask.nonzero(as_tuple=True)[0]

            # Apply capacity factor
            capacity = int(N * self.config.capacity_factor / self.num_experts)
            if len(token_indices) > capacity:
                token_indices = token_indices[:capacity]

            expert_input = x_flat[token_indices]
            expert_output = self.experts[expert_idx](expert_input)

            # Compute weights for this expert
            for k in range(self.top_k):
                k_mask = indices[token_indices, k] == expert_idx
                if k_mask.any():
                    k_indices = token_indices[k_mask]
                    k_weights = weights[k_indices, k].unsqueeze(-1)
                    output[k_indices] += expert_output[k_mask] * k_weights

        output = output.reshape(B, S, D) + residual

        # Load balancing loss
        load_balance_loss = self._load_balance_loss(logits, indices)

        # Expert utilization statistics
        router_probs = F.softmax(logits, dim=-1)
        expert_usage = torch.zeros(self.num_experts, device=x.device)
        for k in range(self.top_k):
            for e in range(self.num_experts):
                expert_usage[e] += (indices[:, k] == e).float().sum()
        expert_usage = expert_usage / (N * self.top_k)

        return {
            "output": output,
            "load_balance_loss": load_balance_loss * self.config.load_balance_weight,
            "expert_usage": expert_usage,
            "router_entropy": -(router_probs * (router_probs + 1e-10).log()).sum(dim=-1).mean(),
        }

    def _load_balance_loss(self, logits: torch.Tensor,
                           indices: torch.Tensor) -> torch.Tensor:
        """Compute auxiliary loss for balanced expert utilization."""
        N = logits.shape[0]
        router_probs = F.softmax(logits, dim=-1)

        # Fraction of tokens routed to each expert
        expert_mask = F.one_hot(indices[:, 0], self.num_experts).float()
        tokens_per_expert = expert_mask.mean(dim=0)

        # Average router probability for each expert
        router_prob_per_expert = router_probs.mean(dim=0)

        # Load balance loss: minimize variance in expert utilization
        loss = (tokens_per_expert * router_prob_per_expert).sum() * self.num_experts
        return loss


class MoETransformerBlock(nn.Module):
    """Transformer block with MoE feed-forward replacement."""

    def __init__(self, dim: int = 768, heads: int = 12,
                 moe_config: MoEConfig = None):
        super().__init__()
        if moe_config is None:
            moe_config = MoEConfig(expert_dim=dim)

        self.attn_norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.moe = OmniMixtureOfExperts(moe_config)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        # Self-attention
        normed = self.attn_norm(x)
        attn_out, _ = self.attn(normed, normed, normed, key_padding_mask=mask)
        x = x + attn_out

        # MoE feed-forward
        moe_result = self.moe(x)

        return {
            "output": moe_result["output"],
            "load_balance_loss": moe_result["load_balance_loss"],
            "expert_usage": moe_result["expert_usage"],
        }
