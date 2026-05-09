"""
moe_sparse_upcycling.py — Sparse Upcycling: Dense to MoE Conversion
Reference: Google Brain "Sparse Upcycling" (2022)
Layer: Compute / AI — MoE Model Construction

Converts a pre-trained dense model into an MoE model by:
1. Copying the FFN weights into multiple experts
2. Training a router from scratch
3. Progressively increasing sparsity
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, List
from dataclasses import dataclass
import copy
import logging

logger = logging.getLogger(__name__)


@dataclass
class UpcyclingConfig:
    num_experts: int = 8
    top_k: int = 2
    noise_std: float = 0.01  # noise added to expert copies
    router_lr_multiplier: float = 10.0  # higher LR for router
    warmup_steps: int = 1000
    sparsity_schedule: str = "linear"  # linear, cosine, step


class ExpertFromDense(nn.Module):
    """Expert created by copying a dense FFN with perturbation."""
    def __init__(self, dense_ffn: nn.Module, noise_std: float = 0.01):
        super().__init__()
        self.ffn = copy.deepcopy(dense_ffn)
        # Add small noise to break symmetry
        with torch.no_grad():
            for param in self.ffn.parameters():
                param.add_(torch.randn_like(param) * noise_std)

    def forward(self, x):
        return self.ffn(x)


class UpcycledMoELayer(nn.Module):
    """MoE layer created from a dense FFN via sparse upcycling."""
    def __init__(self, dense_ffn: nn.Module, dim: int, config: UpcyclingConfig):
        super().__init__()
        self.config = config
        self.num_experts = config.num_experts
        self.top_k = config.top_k

        # Create experts by copying the dense FFN
        self.experts = nn.ModuleList([
            ExpertFromDense(dense_ffn, config.noise_std)
            for _ in range(config.num_experts)
        ])

        # Fresh router (trained from scratch)
        self.gate = nn.Linear(dim, config.num_experts, bias=False)
        nn.init.kaiming_uniform_(self.gate.weight)

        # Keep the original dense FFN as a "shared expert"
        self.shared_expert = copy.deepcopy(dense_ffn)

        self._step = 0

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        B, S, D = x.shape
        flat = x.reshape(-1, D)

        # Compute routing
        logits = self.gate(flat)
        probs = F.softmax(logits, dim=-1)
        topk_w, topk_idx = torch.topk(probs, self.top_k, dim=-1)
        topk_w = topk_w / topk_w.sum(dim=-1, keepdim=True).clamp(min=1e-8)

        # Shared expert (always active during early training)
        shared_out = self.shared_expert(flat)

        # MoE output
        moe_out = torch.zeros_like(flat)
        for e in range(self.num_experts):
            mask = (topk_idx == e).any(dim=-1)
            if not mask.any():
                continue
            tok = mask.nonzero(as_tuple=True)[0]
            e_out = self.experts[e](flat[tok])
            for k in range(self.top_k):
                km = topk_idx[tok, k] == e
                if km.any():
                    ki = tok[km]
                    moe_out[ki] += e_out[km] * topk_w[ki, k].unsqueeze(-1)

        # Interpolate between shared and MoE (gradually increase MoE weight)
        alpha = self._get_moe_weight()
        output = (1 - alpha) * shared_out + alpha * moe_out
        output = output.reshape(B, S, D)

        # Load balance loss
        f = F.one_hot(topk_idx[:, 0], self.num_experts).float().mean(0)
        p = probs.mean(0)
        aux = (f * p).sum() * self.num_experts * 0.01

        self._step += 1

        return {
            "output": output,
            "aux_loss": aux,
            "moe_weight": alpha,
            "router_entropy": -(probs * (probs + 1e-8).log()).sum(-1).mean().item(),
        }

    def _get_moe_weight(self) -> float:
        """Get interpolation weight based on sparsity schedule."""
        progress = min(1.0, self._step / max(self.config.warmup_steps, 1))
        if self.config.sparsity_schedule == "linear":
            return progress
        elif self.config.sparsity_schedule == "cosine":
            import math
            return 0.5 * (1 - math.cos(math.pi * progress))
        elif self.config.sparsity_schedule == "step":
            return 1.0 if progress >= 1.0 else 0.0
        return progress


class SparseUpcycler:
    """Converts a full dense model to MoE."""
    def __init__(self, config: UpcyclingConfig):
        self.config = config

    def upcycle_model(self, model: nn.Module, dim: int) -> nn.Module:
        """Replace all FFN layers in the model with MoE layers."""
        count = 0
        for name, module in model.named_children():
            if self._is_ffn_layer(module):
                moe_layer = UpcycledMoELayer(module, dim, self.config)
                setattr(model, name, moe_layer)
                count += 1
                logger.info(f"Upcycled '{name}' to MoE ({self.config.num_experts} experts)")
            else:
                self.upcycle_model(module, dim)

        if count > 0:
            logger.info(f"Total layers upcycled: {count}")
        return model

    def get_param_groups(self, model: nn.Module, base_lr: float) -> List[Dict]:
        """Create optimizer parameter groups with higher LR for routers."""
        router_params = []
        other_params = []
        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue
            if 'gate' in name:
                router_params.append(param)
            else:
                other_params.append(param)

        return [
            {"params": other_params, "lr": base_lr},
            {"params": router_params, "lr": base_lr * self.config.router_lr_multiplier},
        ]

    def _is_ffn_layer(self, module: nn.Module) -> bool:
        children = list(module.children())
        if len(children) < 2:
            return False
        has_linear = sum(1 for c in children if isinstance(c, nn.Linear)) >= 2
        return has_linear
