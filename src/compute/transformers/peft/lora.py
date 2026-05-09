"""
OMNI Transformer — LoRA (Low-Rank Adaptation) Module
Parameter-efficient fine-tuning for large language models.
Learned from: microsoft/LoRA, Shekswess/tiny-reasoning-language-model (TRL)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class LoRALinear(nn.Module):
    """Linear layer with LoRA adaptation."""
    def __init__(self, in_features: int, out_features: int, rank: int = 8,
                 alpha: float = 16.0, dropout: float = 0.05, bias: bool = False):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.scaling = alpha / rank

        self.linear = nn.Linear(in_features, out_features, bias=bias)
        self.lora_A = nn.Parameter(torch.zeros(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        self.lora_dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        nn.init.zeros_(self.lora_B)
        self.linear.weight.requires_grad = False
        if self.linear.bias is not None:
            self.linear.bias.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base = self.linear(x)
        lora = self.lora_dropout(x) @ self.lora_A.T @ self.lora_B.T * self.scaling
        return base + lora

    def merge(self) -> None:
        """Merge LoRA weights into base linear layer."""
        self.linear.weight.data += (self.lora_B @ self.lora_A * self.scaling).to(self.linear.weight.dtype)

    def unmerge(self) -> None:
        self.linear.weight.data -= (self.lora_B @ self.lora_A * self.scaling).to(self.linear.weight.dtype)


class LoRAAdapter:
    """Apply LoRA to target modules in a model."""
    @staticmethod
    def apply(model: nn.Module, target_modules: Set[str] = None,
              rank: int = 8, alpha: float = 16.0, dropout: float = 0.05) -> nn.Module:
        if target_modules is None:
            target_modules = {"q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}
        count = 0
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                short_name = name.split(".")[-1]
                if short_name in target_modules:
                    parent_name = ".".join(name.split(".")[:-1])
                    parent = dict(model.named_modules())[parent_name] if parent_name else model
                    lora = LoRALinear(module.in_features, module.out_features, rank, alpha, dropout, module.bias is not None)
                    lora.linear.weight.data = module.weight.data.clone()
                    if module.bias is not None:
                        lora.linear.bias.data = module.bias.data.clone()
                    setattr(parent, short_name, lora)
                    count += 1
        # Freeze non-LoRA parameters
        for name, param in model.named_parameters():
            if "lora_" not in name:
                param.requires_grad = False
        total = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"LoRA applied to {count} layers. Trainable: {trainable}/{total} ({100*trainable/total:.2f}%)")
        return model

    @staticmethod
    def save_lora_weights(model: nn.Module, path: str) -> None:
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        lora_state = {k: v for k, v in model.state_dict().items() if "lora_" in k}
        torch.save(lora_state, path)
        logger.info(f"LoRA weights saved: {path} ({len(lora_state)} tensors)")

    @staticmethod
    def load_lora_weights(model: nn.Module, path: str) -> nn.Module:
        lora_state = torch.load(path, map_location="cpu")
        model.load_state_dict(lora_state, strict=False)
        logger.info(f"LoRA weights loaded from {path}")
        return model
