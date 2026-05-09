"""
OMNI MOTHER: Low-Rank Adaptation (LoRA) for MoE (Production Grade)
Implements merge/unmerge, per-expert injection, lightweight checkpointing.
Ref: arXiv:2106.09685 (Hu et al., 2021)
"""
import logging
import math
from typing import Dict, List, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("OmniLoRA")

class LoRALinear(nn.Module):
    """Drop-in nn.Linear replacement with low-rank adaptation path."""
    def __init__(self, in_f: int, out_f: int, r: int = 8, alpha: float = 16.0,
                 dropout: float = 0.0, bias: bool = False):
        super().__init__()
        self.in_f, self.out_f, self.r = in_f, out_f, r
        self.scaling = alpha / r
        self._merged = False
        self.weight = nn.Parameter(torch.empty(out_f, in_f), requires_grad=False)
        self.bias = nn.Parameter(torch.zeros(out_f), requires_grad=False) if bias else None
        self.lora_A = nn.Parameter(torch.empty(r, in_f))
        self.lora_B = nn.Parameter(torch.zeros(out_f, r))
        self.lora_dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))

    def merge(self):
        if not self._merged:
            self.weight.data.add_((self.lora_B @ self.lora_A) * self.scaling)
            self._merged = True

    def unmerge(self):
        if self._merged:
            self.weight.data.sub_((self.lora_B @ self.lora_A) * self.scaling)
            self._merged = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self._merged:
            return F.linear(x, self.weight, self.bias)
        base = F.linear(x, self.weight, self.bias)
        lora = self.lora_dropout(x) @ self.lora_A.T @ self.lora_B.T * self.scaling
        return base + lora

class LoRAInjector:
    """Injects LoRA adapters into matching nn.Linear layers."""
    def __init__(self, r: int = 8, alpha: float = 16.0, dropout: float = 0.05,
                 targets: Optional[List[str]] = None):
        self.r, self.alpha, self.dropout = r, alpha, dropout
        self.targets = targets or ["q_proj", "v_proj", "w1", "w2"]
        self._injected: List[str] = []

    def inject(self, model: nn.Module) -> nn.Module:
        for name, module in model.named_modules():
            for attr in self.targets:
                if hasattr(module, attr):
                    orig = getattr(module, attr)
                    if isinstance(orig, nn.Linear):
                        lora = LoRALinear(orig.in_features, orig.out_features,
                                          self.r, self.alpha, self.dropout, orig.bias is not None)
                        lora.weight.data.copy_(orig.weight.data)
                        if orig.bias is not None:
                            lora.bias.data.copy_(orig.bias.data)
                        setattr(module, attr, lora)
                        self._injected.append(f"{name}.{attr}")
        for n, p in model.named_parameters():
            if "lora_" not in n:
                p.requires_grad = False
        total = sum(p.numel() for p in model.parameters())
        train = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"LoRA: {len(self._injected)} layers, {train:,}/{total:,} trainable ({100*train/max(total,1):.2f}%)")
        return model

    def merge_all(self, model: nn.Module):
        for m in model.modules():
            if isinstance(m, LoRALinear):
                m.merge()

    def get_state(self, model: nn.Module) -> Dict[str, torch.Tensor]:
        return {n: p.clone() for n, p in model.named_parameters() if "lora_" in n}

    def load_state(self, model: nn.Module, sd: Dict[str, torch.Tensor]):
        md = dict(model.named_parameters())
        for k, v in sd.items():
            if k in md:
                md[k].data.copy_(v)
