"""
moe_soft_routing.py — Soft MoE and Expert Choice Routing
Reference: Soft MoE (Google Brain), Expert Choice routing
Layer: Compute / AI — MoE Routing Variants

Implements alternative MoE routing strategies:
1. Soft MoE: each expert receives a learned weighted combination of all tokens
2. Expert Choice: experts choose tokens instead of tokens choosing experts
3. Hash routing: deterministic routing based on token hash
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional
from dataclasses import dataclass
import math


@dataclass
class SoftMoEConfig:
    dim: int = 768
    num_experts: int = 8
    num_slots_per_expert: int = 1
    ff_dim: int = 3072
    dropout: float = 0.0


class SoftMoELayer(nn.Module):
    """Soft Mixture of Experts — fully differentiable routing.

    Instead of discrete token-to-expert assignment, each expert receives
    a learned weighted combination of all tokens. This eliminates
    token dropping and load imbalance entirely.

    Reference: Puigcerver et al., "From Sparse to Soft Mixtures of Experts" (2023)
    """
    def __init__(self, config: SoftMoEConfig):
        super().__init__()
        self.num_experts = config.num_experts
        self.num_slots = config.num_slots_per_expert
        total_slots = config.num_experts * config.num_slots_per_expert

        # Slot parameters: learnable queries for each expert slot
        self.slot_embed = nn.Parameter(torch.randn(total_slots, config.dim) * 0.02)

        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(config.dim, config.ff_dim, bias=False),
                nn.SiLU(),
                nn.Linear(config.ff_dim, config.dim, bias=False),
                nn.Dropout(config.dropout),
            )
            for _ in range(config.num_experts)
        ])
        self.norm = nn.LayerNorm(config.dim)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        B, S, D = x.shape
        residual = x
        x = self.norm(x)

        # Dispatch weights: softmax over tokens for each slot
        # (B, S, D) @ (D, total_slots) -> (B, S, total_slots)
        logits = torch.matmul(x, self.slot_embed.T)
        dispatch_weights = F.softmax(logits, dim=1)  # normalize over tokens

        # Combine weights for gathering: softmax over slots for each token
        combine_weights = F.softmax(logits, dim=2)  # normalize over slots

        # Compute slot inputs: weighted combination of all tokens
        # (B, total_slots, D) = (B, total_slots, S) @ (B, S, D)
        slot_inputs = torch.matmul(dispatch_weights.transpose(1, 2), x)

        # Process each expert's slots
        slot_outputs = torch.zeros_like(slot_inputs)
        for e_idx in range(self.num_experts):
            s_start = e_idx * self.num_slots
            s_end = s_start + self.num_slots
            slot_outputs[:, s_start:s_end] = self.experts[e_idx](
                slot_inputs[:, s_start:s_end])

        # Combine: weighted sum of slot outputs back to token positions
        # (B, S, D) = (B, S, total_slots) @ (B, total_slots, D)
        output = torch.matmul(combine_weights, slot_outputs)
        output = output + residual

        return {"output": output, "aux_loss": torch.tensor(0.0, device=x.device)}


@dataclass
class ExpertChoiceConfig:
    dim: int = 768
    num_experts: int = 8
    tokens_per_expert: int = 64
    ff_dim: int = 3072
    dropout: float = 0.0


class ExpertChoiceLayer(nn.Module):
    """Expert Choice routing: experts choose tokens.

    Instead of each token selecting its top-k experts, each expert
    selects its top-k tokens. This guarantees perfect load balance
    by construction and simplifies capacity management.

    Reference: Zhou et al., "Mixture-of-Experts with Expert Choice Routing"
    """
    def __init__(self, config: ExpertChoiceConfig):
        super().__init__()
        self.config = config
        self.gate = nn.Linear(config.dim, config.num_experts, bias=False)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(config.dim, config.ff_dim, bias=False),
                nn.SiLU(),
                nn.Linear(config.ff_dim, config.dim, bias=False),
                nn.Dropout(config.dropout),
            )
            for _ in range(config.num_experts)
        ])
        self.norm = nn.LayerNorm(config.dim)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        B, S, D = x.shape
        residual = x
        flat = self.norm(x).reshape(-1, D)
        N = flat.shape[0]

        logits = self.gate(flat)  # (N, num_experts)
        # Transpose: each expert selects top-k tokens
        expert_logits = logits.T  # (num_experts, N)

        tpe = min(self.config.tokens_per_expert, N)
        output = torch.zeros_like(flat)

        for e_idx in range(self.config.num_experts):
            # Expert selects its top-k tokens
            scores = expert_logits[e_idx]
            topk_vals, topk_idx = torch.topk(scores, tpe, dim=-1)
            topk_weights = F.softmax(topk_vals, dim=-1)

            expert_tokens = flat[topk_idx]
            expert_out = self.experts[e_idx](expert_tokens)

            # Scatter back with weights
            output.index_add_(0, topk_idx, expert_out * topk_weights.unsqueeze(-1))

        output = output.reshape(B, S, D) + residual

        # Expert choice guarantees balanced load, but add entropy regularizer
        probs = F.softmax(logits, dim=-1)
        entropy = -(probs * (probs + 1e-8).log()).sum(dim=-1).mean()
        aux_loss = -entropy * 0.001  # encourage diverse routing

        return {"output": output, "aux_loss": aux_loss}


class HashRouter(nn.Module):
    """Deterministic hash-based routing for reproducible MoE inference."""
    def __init__(self, num_experts: int, seed: int = 42):
        super().__init__()
        self.num_experts = num_experts
        self.seed = seed

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Assign tokens to experts based on position hash."""
        B, S, D = x.shape
        # Use position-based hashing for reproducibility
        positions = torch.arange(S, device=x.device).unsqueeze(0).expand(B, -1)
        hashed = (positions * 2654435761 + self.seed) % self.num_experts
        return hashed


class MoERoutingFactory:
    """Factory for creating MoE routing strategies."""
    @staticmethod
    def create(strategy: str, dim: int, num_experts: int, **kwargs):
        if strategy == "soft":
            return SoftMoELayer(SoftMoEConfig(dim=dim, num_experts=num_experts, **kwargs))
        elif strategy == "expert_choice":
            return ExpertChoiceLayer(ExpertChoiceConfig(dim=dim, num_experts=num_experts, **kwargs))
        elif strategy == "hash":
            return HashRouter(num_experts)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")
