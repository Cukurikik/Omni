"""
moe_lora_adapter.py — LoRA Adapters for MoE Expert Fine-Tuning
Layer: Compute / AI — MoE PEFT

Low-Rank Adaptation applied per-expert in MoE models.
Enables efficient fine-tuning where each expert gets its own
LoRA adapter, allowing task-specific specialization with
minimal parameter overhead.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, List
from dataclasses import dataclass
import math


@dataclass
class MoELoRAConfig:
    rank: int = 16
    alpha: float = 32.0
    dropout: float = 0.05
    target_modules: List[str] = None
    per_expert: bool = True
    num_experts: int = 8

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["w1", "w2", "w3"]
        self.scaling = self.alpha / self.rank


class LoRALinear(nn.Module):
    """LoRA adapter for a single linear layer."""
    def __init__(self, in_features, out_features, rank, scaling, dropout=0.0):
        super().__init__()
        self.rank = rank
        self.scaling = scaling
        self.lora_A = nn.Parameter(torch.randn(in_features, rank) * (1.0 / math.sqrt(rank)))
        self.lora_B = nn.Parameter(torch.zeros(rank, out_features))
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, base_output):
        """Add LoRA delta to the base linear output."""
        lora_out = self.dropout(x) @ self.lora_A @ self.lora_B * self.scaling
        return base_output + lora_out

    @property
    def num_parameters(self):
        return self.lora_A.numel() + self.lora_B.numel()


class ExpertLoRAAdapter(nn.Module):
    """LoRA adapter set for a single expert's linear layers."""
    def __init__(self, expert: nn.Module, config: MoELoRAConfig):
        super().__init__()
        self.adapters = nn.ModuleDict()
        for name, module in expert.named_modules():
            if isinstance(module, nn.Linear) and any(
                t in name for t in config.target_modules
            ):
                self.adapters[name.replace(".", "_")] = LoRALinear(
                    module.in_features, module.out_features,
                    config.rank, config.scaling, config.dropout)

    def get_adapter(self, layer_name: str) -> Optional[LoRALinear]:
        key = layer_name.replace(".", "_")
        return self.adapters.get(key)

    @property
    def num_parameters(self):
        return sum(a.num_parameters for a in self.adapters.values())


class MoELoRAManager:
    """Manages LoRA adapters across all experts in an MoE model."""
    def __init__(self, moe_layer: nn.Module, config: MoELoRAConfig):
        self.config = config
        self.expert_adapters: Dict[int, ExpertLoRAAdapter] = {}

        # Freeze base model parameters
        for param in moe_layer.parameters():
            param.requires_grad = False

        # Create per-expert adapters
        if hasattr(moe_layer, 'experts'):
            for e_idx, expert in enumerate(moe_layer.experts):
                adapter = ExpertLoRAAdapter(expert, config)
                self.expert_adapters[e_idx] = adapter

    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get all trainable LoRA parameters."""
        params = []
        for adapter in self.expert_adapters.values():
            params.extend(adapter.parameters())
        return params

    def total_lora_parameters(self) -> int:
        return sum(a.num_parameters for a in self.expert_adapters.values())

    def save_adapters(self, path: str):
        """Save only LoRA weights."""
        state = {}
        for e_idx, adapter in self.expert_adapters.items():
            state[f"expert_{e_idx}"] = adapter.state_dict()
        torch.save(state, path)

    def load_adapters(self, path: str):
        """Load LoRA weights."""
        state = torch.load(path, map_location="cpu", weights_only=True)
        for e_idx, adapter in self.expert_adapters.items():
            key = f"expert_{e_idx}"
            if key in state:
                adapter.load_state_dict(state[key])

    def merge_into_base(self, moe_layer: nn.Module):
        """Merge LoRA weights into base model (for inference)."""
        for e_idx, adapter in self.expert_adapters.items():
            expert = moe_layer.experts[e_idx]
            for name, module in expert.named_modules():
                if isinstance(module, nn.Linear):
                    lora = adapter.get_adapter(name)
                    if lora is not None:
                        delta = (lora.lora_A @ lora.lora_B * lora.scaling).T
                        module.weight.data += delta

    def report(self) -> Dict:
        total_lora = self.total_lora_parameters()
        return {
            "num_experts_with_lora": len(self.expert_adapters),
            "total_lora_params": total_lora,
            "rank": self.config.rank,
            "alpha": self.config.alpha,
            "target_modules": self.config.target_modules,
            "per_expert_params": {
                e: a.num_parameters for e, a in self.expert_adapters.items()
            },
        }
