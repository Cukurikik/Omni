"""
moe_qlora_finetuner.py — Compute / Training
Layer: Compute / AI — QLoRA MoE Finetuning

Inspired by llm-finetuning.
Provides a targeted fine-tuning pipeline using QLoRA specifically designed
to update only specific MoE experts (e.g., teaching the coding expert a new language)
without disrupting the general knowledge experts or causing catastrophic forgetting.
"""

import torch
import torch.nn as nn

class QLoRAMoEAdapter(nn.Module):
    """
    A Low-Rank Adapter that attaches specifically to a frozen 4-bit expert.
    """
    def __init__(self, hidden_dim: int, rank: int, alpha: float):
        super().__init__()
        self.rank = rank
        self.scaling = alpha / rank
        
        self.lora_A = nn.Linear(hidden_dim, rank, bias=False)
        self.lora_B = nn.Linear(rank, hidden_dim, bias=False)
        
        # Initialize
        nn.init.normal_(self.lora_A.weight, std=0.02)
        nn.init.zeros_(self.lora_B.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.lora_B(self.lora_A(x)) * self.scaling

class MoEFinetunePipeline:
    """
    Manages the targeted fine-tuning of specific experts.
    """
    def __init__(self, target_expert_ids: list, lora_rank: int = 8):
        self.target_expert_ids = target_expert_ids
        self.lora_rank = lora_rank
        print(f"[QLoRA] Initializing MoE Fine-Tuning Pipeline. Targeting Experts: {target_expert_ids}")

    def prepare_model_for_finetuning(self, moe_layer: nn.Module) -> nn.Module:
        """
        Freezes the entire MoE layer (and base model), and attaches
        trainable LoRA adapters ONLY to the specified target experts.
        """
        # 1. Freeze everything
        for param in moe_layer.parameters():
            param.requires_grad = False
            
        # 2. Assume moe_layer has an 'experts' ModuleList
        if not hasattr(moe_layer, 'experts'):
            raise ValueError("MoE layer does not expose an 'experts' ModuleList.")
            
        # 3. Attach Adapters
        self.adapters = nn.ModuleDict()
        
        for expert_id in self.target_expert_ids:
            # Get the hidden dimension from the expert (mocking extraction)
            # In a real scenario, this is extracted from expert.in_features
            hidden_dim = moe_layer.experts[expert_id].in_features if hasattr(moe_layer.experts[expert_id], 'in_features') else 4096
            
            adapter = QLoRAMoEAdapter(hidden_dim, self.lora_rank, alpha=16.0)
            self.adapters[str(expert_id)] = adapter
            
        print(f"[QLoRA] Attached {len(self.adapters)} trainable adapters. Base weights remain frozen in 4-bit.")
        return moe_layer

    def forward_expert_with_lora(self, expert_id: int, expert_fn, x: torch.Tensor) -> torch.Tensor:
        """
        Executes the frozen expert, and if a LoRA exists for it, adds the delta.
        """
        base_out = expert_fn(x) # Frozen 4-bit forward pass
        
        adapter_key = str(expert_id)
        if adapter_key in self.adapters:
            lora_delta = self.adapters[adapter_key](x)
            return base_out + lora_delta
            
        return base_out
