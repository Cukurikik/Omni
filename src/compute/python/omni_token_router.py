"""
OMNI MOTHER: Top-K with Shared Experts Router (Production Grade)
Implements DeepSeek-style routing with dedicated shared experts.
Ref: DeepSeek-MoE (2024)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional
import logging

logger = logging.getLogger("OmniTokenRouter")

class SharedExpertFFN(nn.Module):
    """Shared expert that processes ALL tokens unconditionally."""
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.0):
        super().__init__()
        self.gate_proj = nn.Linear(d_model, d_ff, bias=False)
        self.up_proj = nn.Linear(d_model, d_ff, bias=False)
        self.down_proj = nn.Linear(d_ff, d_model, bias=False)
        self.act = nn.SiLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.down_proj(self.act(self.gate_proj(x)) * self.up_proj(x)))

class RoutedExpertFFN(nn.Module):
    """Single routed expert with SwiGLU activation."""
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.0):
        super().__init__()
        self.gate_proj = nn.Linear(d_model, d_ff, bias=False)
        self.up_proj = nn.Linear(d_model, d_ff, bias=False)
        self.down_proj = nn.Linear(d_ff, d_model, bias=False)
        self.act = nn.SiLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.down_proj(self.act(self.gate_proj(x)) * self.up_proj(x)))

class TopKSharedRouter(nn.Module):
    """Top-K gate selecting K routed experts plus always-on shared experts."""
    def __init__(self, d_model: int, num_routed: int, k: int = 2, jitter: float = 0.01):
        super().__init__()
        self.k = k
        self.jitter = jitter
        self.gate = nn.Linear(d_model, num_routed, bias=False)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Returns (topk_scores, topk_indices, full_probs) all over [num_tokens, ...]."""
        if x.dim() == 3:
            x = x.view(-1, x.size(-1))
        logits = self.gate(x)
        if self.training and self.jitter > 0:
            noise = torch.empty_like(logits).uniform_(1 - self.jitter, 1 + self.jitter)
            logits = logits * noise
        probs = F.softmax(logits, dim=-1)
        topk_scores, topk_indices = torch.topk(probs, self.k, dim=-1)
        topk_scores = topk_scores / topk_scores.sum(dim=-1, keepdim=True).clamp(min=1e-8)
        return topk_scores, topk_indices, probs

class DeepSeekMoELayer(nn.Module):
    """
    Full MoE layer with N shared + M routed experts.
    Shared experts always fire. Routed experts are gated top-K.
    """
    def __init__(self, d_model: int = 2048, d_ff: int = 1408,
                 num_routed: int = 64, num_shared: int = 2, k: int = 6,
                 dropout: float = 0.0, aux_loss_weight: float = 0.01):
        super().__init__()
        self.num_routed = num_routed
        self.num_shared = num_shared
        self.aux_weight = aux_loss_weight
        self.router = TopKSharedRouter(d_model, num_routed, k)
        self.shared_experts = nn.ModuleList([SharedExpertFFN(d_model, d_ff, dropout) for _ in range(num_shared)])
        self.routed_experts = nn.ModuleList([RoutedExpertFFN(d_model, d_ff, dropout) for _ in range(num_routed)])
        self.norm = nn.LayerNorm(d_model)

    def _aux_loss(self, probs: torch.Tensor, indices: torch.Tensor) -> torch.Tensor:
        mask = F.one_hot(indices, self.num_routed).float().sum(dim=1)
        f = mask.mean(dim=0)
        p = probs.mean(dim=0)
        return self.num_routed * (f * p).sum()

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        B, S, D = x.shape
        residual = x
        normed = self.norm(x)
        flat = normed.view(-1, D)

        # Shared experts (always active)
        shared_out = sum(expert(flat) for expert in self.shared_experts)

        # Routed experts
        topk_scores, topk_indices, full_probs = self.router(normed)
        routed_out = torch.zeros_like(flat)
        for i in range(self.router.k):
            scores_i = topk_scores[:, i].unsqueeze(-1)
            indices_i = topk_indices[:, i]
            for eid in range(self.num_routed):
                mask = indices_i == eid
                if mask.any():
                    expert_input = flat[mask]
                    routed_out[mask] += scores_i[mask] * self.routed_experts[eid](expert_input)

        combined = shared_out + routed_out
        output = residual + combined.view(B, S, D)
        aux = self._aux_loss(full_probs, topk_indices) * self.aux_weight
        return output, aux
