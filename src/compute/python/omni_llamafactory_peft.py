import torch
import torch.nn as nn
from typing import List, Dict

class OmniLoRALayer(nn.Module):
    """
    Low-Rank Adaptation (LoRA) layer for Parameter-Efficient Fine-Tuning.
    """
    def __init__(self, in_features: int, out_features: int, rank: int = 8, alpha: float = 16.0, dropout: float = 0.05):
        super().__init__()
        self.rank = rank
        self.scaling = alpha / rank
        
        self.lora_A = nn.Parameter(torch.zeros((in_features, rank)))
        self.lora_B = nn.Parameter(torch.zeros((rank, out_features)))
        self.dropout = nn.Dropout(dropout)
        
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(x) @ self.lora_A @ self.lora_B * self.scaling

def apply_lora_to_moe(model: nn.Module, target_modules: List[str], rank: int = 8) -> nn.Module:
    """
    Applies LoRA dynamically to the Expert Linear layers in an MoE architecture.
    Inspired by LlamaFactory's PEFT integration.
    """
    num_injections = 0
    
    for name, module in model.named_modules():
        if any(target in name for target in target_modules) and isinstance(module, nn.Linear):
            # Create a wrapper module that computes Linear + LoRA
            class LoRAWrapper(nn.Module):
                def __init__(self, base_layer: nn.Linear, lora_layer: OmniLoRALayer):
                    super().__init__()
                    self.base_layer = base_layer
                    self.lora_layer = lora_layer
                    # Freeze base layer weights
                    self.base_layer.weight.requires_grad = False
                    if self.base_layer.bias is not None:
                        self.base_layer.bias.requires_grad = False
                        
                def forward(self, x):
                    return self.base_layer(x) + self.lora_layer(x)
            
            lora = OmniLoRALayer(module.in_features, module.out_features, rank=rank)
            wrapper = LoRAWrapper(module, lora)
            
            # Sub-module replacement trick
            parent_name = name.rsplit('.', 1)[0] if '.' in name else ''
            child_name = name.rsplit('.', 1)[-1]
            if parent_name == '':
                setattr(model, child_name, wrapper)
            else:
                parent = model.get_submodule(parent_name)
                setattr(parent, child_name, wrapper)
                
            num_injections += 1

    print(f"OMNI Python (PEFT): Injected LoRA adapters into {num_injections} MoE expert layers.")
    return model

import math
