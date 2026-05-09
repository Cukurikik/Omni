"""
moe_multimodal_router.py — Multimodal-Aware Expert Router
Layer: Compute / AI — MoE Multimodal Routing

Router that considers input modality (text, image, audio, code) when
selecting experts. Different modalities are biased toward specialized
experts while maintaining shared expert access for cross-modal tasks.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum


class Modality(IntEnum):
    TEXT = 0
    IMAGE = 1
    AUDIO = 2
    CODE = 3
    VIDEO = 4
    TABLE = 5


@dataclass
class MultimodalRouterConfig:
    dim: int = 1024
    num_experts: int = 16
    num_shared_experts: int = 2
    top_k: int = 2
    num_modalities: int = 6
    modality_bias_scale: float = 0.5
    diversity_penalty: float = 0.01


class ModalityEncoder(nn.Module):
    """Encodes modality information into routing bias."""
    def __init__(self, num_modalities, num_experts, scale=0.5):
        super().__init__()
        self.affinity = nn.Parameter(
            torch.randn(num_modalities, num_experts) * 0.02)
        self.scale = scale

    def forward(self, modality_ids: torch.Tensor) -> torch.Tensor:
        """Return per-token modality bias for routing.

        Args:
            modality_ids: (N,) integer tensor of modality IDs
        Returns:
            bias: (N, num_experts) routing bias
        """
        return self.affinity[modality_ids] * self.scale


class MultimodalRouter(nn.Module):
    """Router that incorporates modality information."""
    def __init__(self, config: MultimodalRouterConfig):
        super().__init__()
        self.config = config
        self.gate = nn.Linear(config.dim, config.num_experts, bias=False)
        self.modality_encoder = ModalityEncoder(
            config.num_modalities, config.num_experts,
            config.modality_bias_scale)
        self.num_experts = config.num_experts
        self.top_k = config.top_k

    def forward(
        self,
        x: torch.Tensor,
        modality_ids: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Route tokens with modality awareness.

        Returns:
            weights: (N, top_k) normalized expert weights
            indices: (N, top_k) selected expert IDs
            logits: (N, num_experts) raw routing logits
        """
        logits = self.gate(x)

        # Add modality bias
        if modality_ids is not None:
            bias = self.modality_encoder(modality_ids)
            logits = logits + bias

        probs = F.softmax(logits, dim=-1)
        topk_w, topk_idx = torch.topk(probs, self.top_k, dim=-1)
        topk_w = topk_w / topk_w.sum(dim=-1, keepdim=True).clamp(min=1e-8)

        return topk_w, topk_idx, logits


class MultimodalMoELayer(nn.Module):
    """MoE layer with modality-aware routing and shared experts."""
    def __init__(self, config: MultimodalRouterConfig):
        super().__init__()
        self.config = config
        self.norm = nn.RMSNorm(config.dim)
        self.router = MultimodalRouter(config)

        # Shared experts (process all tokens regardless of modality)
        self.shared_experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(config.dim, config.dim * 4, bias=False),
                nn.SiLU(),
                nn.Linear(config.dim * 4, config.dim, bias=False),
            )
            for _ in range(config.num_shared_experts)
        ])

        # Routed experts (modality-biased selection)
        self.routed_experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(config.dim, config.dim * 4, bias=False),
                nn.SiLU(),
                nn.Linear(config.dim * 4, config.dim, bias=False),
            )
            for _ in range(config.num_experts)
        ])

    def forward(
        self,
        x: torch.Tensor,
        modality_ids: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        B, S, D = x.shape
        residual = x
        normed = self.norm(x)
        flat = normed.reshape(-1, D)
        N = flat.shape[0]

        # Flatten modality IDs
        if modality_ids is not None:
            if modality_ids.dim() == 1 and modality_ids.shape[0] == B:
                flat_mod = modality_ids.unsqueeze(1).expand(B, S).reshape(-1)
            else:
                flat_mod = modality_ids.reshape(-1)
        else:
            flat_mod = None

        # Shared expert output
        shared_out = sum(exp(flat) for exp in self.shared_experts)

        # Router with modality awareness
        weights, indices, logits = self.router(flat, flat_mod)

        # Routed expert output
        routed_out = torch.zeros_like(flat)
        for e in range(self.config.num_experts):
            mask = (indices == e).any(dim=-1)
            if not mask.any():
                continue
            tok = mask.nonzero(as_tuple=True)[0]
            e_out = self.routed_experts[e](flat[tok])
            for k in range(self.config.top_k):
                km = indices[tok, k] == e
                if km.any():
                    ki = tok[km]
                    routed_out[ki] += e_out[km] * weights[ki, k].unsqueeze(-1)

        output = (shared_out + routed_out).reshape(B, S, D) + residual

        # Compute auxiliary losses
        probs = F.softmax(logits, dim=-1)
        f = F.one_hot(indices[:, 0], self.config.num_experts).float().mean(0)
        p = probs.mean(0)
        aux_loss = (f * p).sum() * self.config.num_experts * 0.01

        # Modality diversity: encourage each modality to use diverse experts
        diversity_loss = torch.tensor(0.0, device=x.device)
        if flat_mod is not None:
            for mod in range(self.config.num_modalities):
                mod_mask = flat_mod == mod
                if mod_mask.sum() > 0:
                    mod_probs = probs[mod_mask].mean(0)
                    ent = -(mod_probs * (mod_probs + 1e-8).log()).sum()
                    diversity_loss = diversity_loss - ent  # maximize entropy

        total_aux = aux_loss + self.config.diversity_penalty * diversity_loss

        # Per-modality routing statistics
        modality_stats = {}
        if flat_mod is not None:
            for mod in Modality:
                mod_mask = flat_mod == mod.value
                if mod_mask.sum() > 0:
                    mod_indices = indices[mod_mask, 0]
                    usage = torch.zeros(self.config.num_experts, device=x.device)
                    for e in range(self.config.num_experts):
                        usage[e] = (mod_indices == e).float().sum()
                    modality_stats[mod.name] = (usage / mod_mask.sum()).tolist()

        return {
            "output": output,
            "aux_loss": total_aux,
            "router_logits": logits,
            "modality_stats": modality_stats,
        }
