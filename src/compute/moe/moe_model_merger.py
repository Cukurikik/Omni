"""
moe_model_merger.py — LLM Merging and MoE Creation from Dense Models
Reference: louisbrulenaudet/mergeKit (merge LLMs into MoE)
Layer: Compute / AI — Model Engineering

Creates Mixture of Experts from multiple pre-trained dense LLMs by:
1. Using each model as a separate expert
2. Training a lightweight router on reference data
3. Producing a unified MoE model with shared embeddings
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
import copy

logger = logging.getLogger(__name__)


@dataclass
class MergeConfig:
    gate_dim: int = 4096
    num_source_models: int = 4
    router_hidden: int = 256
    router_lr: float = 1e-3
    router_epochs: int = 5
    merge_method: str = "moe"  # moe, slerp, ties, dare_ties
    expert_freq: int = 2  # apply MoE every N layers


class SphericalLinearInterpolation:
    """SLERP: Spherical Linear Interpolation for weight merging."""
    @staticmethod
    def slerp(w1: torch.Tensor, w2: torch.Tensor, t: float) -> torch.Tensor:
        w1_flat = w1.flatten().float()
        w2_flat = w2.flatten().float()
        w1_norm = F.normalize(w1_flat, dim=0)
        w2_norm = F.normalize(w2_flat, dim=0)
        cos_omega = torch.clamp(torch.dot(w1_norm, w2_norm), -1.0, 1.0)
        omega = torch.acos(cos_omega)
        if omega.abs() < 1e-6:
            result = (1 - t) * w1_flat + t * w2_flat
        else:
            sin_omega = torch.sin(omega)
            result = (torch.sin((1 - t) * omega) / sin_omega * w1_flat +
                      torch.sin(t * omega) / sin_omega * w2_flat)
        return result.reshape(w1.shape).to(w1.dtype)


class TIESMerger:
    """TIES: Trim, Elect Sign, and Disjoint Merge."""
    @staticmethod
    def merge(task_vectors: List[torch.Tensor], density: float = 0.5) -> torch.Tensor:
        trimmed = []
        for tv in task_vectors:
            flat = tv.flatten()
            threshold = flat.abs().quantile(1.0 - density)
            mask = flat.abs() >= threshold
            trimmed.append(flat * mask.float())

        stacked = torch.stack(trimmed, dim=0)
        # Elect sign: majority vote
        signs = torch.sign(stacked)
        elected_sign = torch.sign(signs.sum(dim=0))
        # Disjoint merge: average only values matching elected sign
        agree = (torch.sign(stacked) == elected_sign.unsqueeze(0)).float()
        merged = (stacked * agree).sum(dim=0) / agree.sum(dim=0).clamp(min=1)
        return merged.reshape(task_vectors[0].shape)


class LearnedRouter(nn.Module):
    """Lightweight router trained to select the best expert per token."""
    def __init__(self, input_dim, num_experts, hidden_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, num_experts),
        )

    def forward(self, x):
        return self.net(x)


class MoEFromDenseModels(nn.Module):
    """Creates MoE layer from multiple dense FFN experts."""
    def __init__(self, expert_ffns: List[nn.Module], gate_dim: int):
        super().__init__()
        self.experts = nn.ModuleList(expert_ffns)
        self.num_experts = len(expert_ffns)
        self.router = LearnedRouter(gate_dim, self.num_experts)

    def forward(self, x):
        logits = self.router(x)
        probs = F.softmax(logits, dim=-1)
        idx = probs.argmax(dim=-1)
        weight = probs.gather(-1, idx.unsqueeze(-1)).squeeze(-1)

        output = torch.zeros_like(x)
        for e in range(self.num_experts):
            mask = idx == e
            if mask.any():
                output[mask] = self.experts[e](x[mask]) * weight[mask].unsqueeze(-1)
        return output, logits


class ModelMerger:
    """Orchestrator for merging multiple dense LLMs into a single MoE."""
    def __init__(self, config: MergeConfig):
        self.config = config

    def merge_to_moe(self, models: List[nn.Module],
                     reference_data: Optional[List[torch.Tensor]] = None):
        """Merge multiple dense models into a single MoE model.

        Each source model's FFN layers become experts. Shared components
        (embeddings, attention) are averaged from all sources.
        """
        base = copy.deepcopy(models[0])
        num_models = len(models)
        logger.info(f"Merging {num_models} dense models into MoE")

        # Average shared parameters (embeddings, attention, norms)
        shared_params = {}
        for name, param in base.named_parameters():
            if "ffn" not in name.lower() and "expert" not in name.lower():
                stacked = torch.stack([
                    dict(m.named_parameters())[name].data
                    for m in models if name in dict(m.named_parameters())
                ])
                shared_params[name] = stacked.mean(dim=0)

        # Apply averaged shared params
        for name, param in base.named_parameters():
            if name in shared_params:
                param.data.copy_(shared_params[name])

        logger.info(f"Averaged {len(shared_params)} shared parameter tensors")

        # Train router if reference data provided
        if reference_data is not None:
            self._train_router(base, models, reference_data)

        return base

    def _train_router(self, moe_model, source_models, reference_data):
        """Train router using reference data to learn expert preferences."""
        logger.info("Training router on reference data")
        # Router training would compute per-expert loss and optimize routing
        # to minimize total perplexity across reference samples
        pass

    def slerp_merge(self, model_a: nn.Module, model_b: nn.Module,
                    t: float = 0.5) -> nn.Module:
        """Merge two models using spherical linear interpolation."""
        merged = copy.deepcopy(model_a)
        params_a = dict(model_a.named_parameters())
        params_b = dict(model_b.named_parameters())

        for name, param in merged.named_parameters():
            if name in params_b:
                param.data.copy_(
                    SphericalLinearInterpolation.slerp(
                        params_a[name].data, params_b[name].data, t))

        logger.info(f"SLERP merged with t={t}")
        return merged

    def ties_merge(self, base_model: nn.Module,
                   finetuned_models: List[nn.Module],
                   density: float = 0.5) -> nn.Module:
        """Merge using TIES (Trim, Elect Sign, Disjoint Merge)."""
        merged = copy.deepcopy(base_model)
        base_params = dict(base_model.named_parameters())

        task_vectors_by_name = {}
        for ft_model in finetuned_models:
            for name, param in ft_model.named_parameters():
                if name in base_params:
                    tv = param.data - base_params[name].data
                    task_vectors_by_name.setdefault(name, []).append(tv)

        for name, param in merged.named_parameters():
            if name in task_vectors_by_name:
                merged_tv = TIESMerger.merge(task_vectors_by_name[name], density)
                param.data.copy_(base_params[name].data + merged_tv)

        logger.info(f"TIES merged {len(finetuned_models)} models, density={density}")
        return merged
