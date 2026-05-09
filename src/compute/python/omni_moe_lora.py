import torch
import torch.nn as nn

# OMNI MOTHER: LoRA Adapters for MoE Experts
# Parameter-efficient fine-tuning for individual experts

class OmniExpertLoRA(nn.Module):
    def __init__(self, base_layer: nn.Linear, rank: int = 8, alpha: float = 16.0):
        super().__init__()
        self.base_layer = base_layer
        self.base_layer.weight.requires_grad = False
        
        in_dim = base_layer.in_features
        out_dim = base_layer.out_features
        
        self.lora_A = nn.Linear(in_dim, rank, bias=False)
        self.lora_B = nn.Linear(rank, out_dim, bias=False)
        self.scaling = alpha / rank

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base_layer(x) + self.lora_B(self.lora_A(x)) * self.scaling
