"""
moe_mixture_deepseek.py — DeepSeek-V3 Style MoE with Fine-Grained Experts
Reference: DeepSeek-V3 architecture (256 experts, 8 active)
Layer: Compute / AI — MoE Architecture Variant

Implements DeepSeek-style fine-grained MoE with:
- Large number of small experts (256+)
- Shared expert for all tokens
- Auxiliary-loss-free load balancing via bias terms
- Multi-head latent attention (MLA) compatibility
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DeepSeekMoEConfig:
    dim: int = 2048
    num_routed_experts: int = 256
    num_shared_experts: int = 2
    top_k: int = 8
    ff_dim_per_expert: int = 1408  # small expert size
    shared_ff_dim: int = 2816
    dropout: float = 0.0
    use_bias_correction: bool = True  # auxiliary-loss-free balancing
    bias_update_rate: float = 0.001


class SharedExpert(nn.Module):
    """Shared expert that processes all tokens unconditionally."""
    def __init__(self, dim, ff_dim, dropout=0.0):
        super().__init__()
        self.gate_proj = nn.Linear(dim, ff_dim, bias=False)
        self.up_proj = nn.Linear(dim, ff_dim, bias=False)
        self.down_proj = nn.Linear(ff_dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x)))


class FineGrainedExpert(nn.Module):
    """Small expert module for fine-grained MoE."""
    def __init__(self, dim, ff_dim, dropout=0.0):
        super().__init__()
        self.gate_proj = nn.Linear(dim, ff_dim, bias=False)
        self.up_proj = nn.Linear(dim, ff_dim, bias=False)
        self.down_proj = nn.Linear(ff_dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x)))


class AuxLossFreeRouter(nn.Module):
    """Router with learnable bias for auxiliary-loss-free load balancing.

    Instead of adding an auxiliary loss term, uses per-expert bias
    adjustments that are updated based on expert utilization statistics.
    Over-utilized experts get negative bias, under-utilized get positive.
    """
    def __init__(self, dim, num_experts, top_k, bias_rate=0.001):
        super().__init__()
        self.gate = nn.Linear(dim, num_experts, bias=False)
        self.top_k = top_k
        self.num_experts = num_experts
        self.bias_rate = bias_rate

        # Expert selection bias (not learned by gradient, updated by usage)
        self.register_buffer("expert_bias", torch.zeros(num_experts))
        self.register_buffer("expert_counts", torch.zeros(num_experts))
        self.register_buffer("total_count", torch.tensor(0.0))

    @torch.no_grad()
    def update_bias(self, indices: torch.Tensor):
        """Update expert bias based on recent utilization."""
        N = indices.shape[0]
        self.total_count += N

        counts = torch.zeros(self.num_experts, device=indices.device)
        for k in range(indices.shape[1]):
            for e in range(self.num_experts):
                counts[e] += (indices[:, k] == e).sum()

        self.expert_counts += counts
        target = N * self.top_k / self.num_experts
        deviation = counts - target
        self.expert_bias -= self.bias_rate * deviation

    def forward(self, x):
        logits = self.gate(x)
        # Add bias for load balancing (no gradient through bias)
        adjusted_logits = logits + self.expert_bias.detach()

        topk_vals, topk_idx = torch.topk(adjusted_logits, self.top_k, dim=-1)
        # Use original logits (without bias) for weight computation
        original_vals = logits.gather(-1, topk_idx)
        topk_weights = F.softmax(original_vals, dim=-1)

        return topk_weights, topk_idx, logits


class DeepSeekMoELayer(nn.Module):
    """DeepSeek-V3 style MoE layer with shared + routed experts."""
    def __init__(self, config: DeepSeekMoEConfig):
        super().__init__()
        self.config = config
        self.norm = nn.RMSNorm(config.dim)

        # Shared experts (always active for all tokens)
        self.shared_experts = nn.ModuleList([
            SharedExpert(config.dim, config.shared_ff_dim, config.dropout)
            for _ in range(config.num_shared_experts)
        ])

        # Routed experts (sparse activation)
        self.routed_experts = nn.ModuleList([
            FineGrainedExpert(config.dim, config.ff_dim_per_expert, config.dropout)
            for _ in range(config.num_routed_experts)
        ])

        self.router = AuxLossFreeRouter(
            config.dim, config.num_routed_experts,
            config.top_k, config.bias_update_rate)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        B, S, D = x.shape
        residual = x
        normed = self.norm(x)
        flat = normed.reshape(-1, D)

        # Shared expert output (always computed)
        shared_out = sum(expert(flat) for expert in self.shared_experts)

        # Router
        weights, indices, logits = self.router(flat)

        # Update bias during training
        if self.training and self.config.use_bias_correction:
            self.router.update_bias(indices)

        # Routed expert output
        routed_out = torch.zeros_like(flat)
        for e_idx in range(self.config.num_routed_experts):
            mask = (indices == e_idx).any(dim=-1)
            if not mask.any():
                continue
            tok_idx = mask.nonzero(as_tuple=True)[0]
            e_out = self.routed_experts[e_idx](flat[tok_idx])
            for k in range(self.config.top_k):
                km = indices[tok_idx, k] == e_idx
                if km.any():
                    ki = tok_idx[km]
                    routed_out[ki] += e_out[km] * weights[ki, k].unsqueeze(-1)

        # Combine shared + routed
        output = (shared_out + routed_out).reshape(B, S, D) + residual

        # Expert utilization stats
        usage = torch.zeros(self.config.num_routed_experts, device=x.device)
        for k in range(self.config.top_k):
            for e in range(self.config.num_routed_experts):
                usage[e] += (indices[:, k] == e).float().sum()

        return {
            "output": output,
            "aux_loss": torch.tensor(0.0, device=x.device),  # loss-free!
            "expert_usage": usage / (flat.shape[0] * self.config.top_k),
            "router_logits": logits,
        }
