"""
micro_kiki_lora_router.py — Compute / Cognitive Layer
Layer: Compute / AI — Multi-Domain LoRA Routing

Inspired by the 'micro-kiki' architecture (35 domain-expert LoRAs on Qwen).
Instead of full-weight experts, this module dynamically routes hidden states
to a massive array of specialized LoRA adapters, drastically reducing VRAM
requirements while maintaining high domain specialization.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Dict

class LoRAExpert(nn.Module):
    """A single low-rank adaptation expert."""
    def __init__(self, hidden_dim: int, rank: int = 16):
        super().__init__()
        self.lora_A = nn.Linear(hidden_dim, rank, bias=False)
        self.lora_B = nn.Linear(rank, hidden_dim, bias=False)
        
        # Initialization mimicking standard LoRA (A=kaiming, B=zero)
        nn.init.kaiming_uniform_(self.lora_A.weight, a=torch.sqrt(torch.tensor(5.0)))
        nn.init.zeros_(self.lora_B.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.lora_B(self.lora_A(x))

class MicroKikiLoRARouter(nn.Module):
    """
    Routes tokens to specific LoRA adapters based on a gating network.
    """
    def __init__(self, hidden_dim: int, num_loras: int = 35, rank: int = 16, top_k: int = 2):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_loras = num_loras
        self.top_k = top_k
        
        # The gating network that decides which LoRA experts to use
        self.gate = nn.Linear(hidden_dim, num_loras, bias=False)
        
        # ModuleDict to hold our 35 domain-specific LoRA experts
        self.experts = nn.ModuleList([LoRAExpert(hidden_dim, rank) for _ in range(num_loras)])

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """
        hidden_states: (Batch, SeqLen, HiddenDim)
        """
        batch_size, seq_len, hidden_dim = hidden_states.shape
        flat_x = hidden_states.view(-1, hidden_dim)
        
        # Calculate routing probabilities
        logits = self.gate(flat_x)
        routing_weights = F.softmax(logits, dim=-1)
        
        # Select Top-K experts
        topk_weights, topk_indices = torch.topk(routing_weights, self.top_k, dim=-1)
        
        # Normalize weights so they sum to 1.0 across the selected experts
        topk_weights = topk_weights / topk_weights.sum(dim=-1, keepdim=True)
        
        # Prepare output tensor
        final_output = torch.zeros_like(flat_x)
        
        # For each token, compute the LoRA delta and apply routing weights
        for i in range(flat_x.shape[0]):
            token_x = flat_x[i].unsqueeze(0)
            token_out = torch.zeros_like(token_x)
            
            for k in range(self.top_k):
                expert_idx = topk_indices[i, k].item()
                weight = topk_weights[i, k].item()
                
                # Compute LoRA delta and accumulate
                lora_delta = self.experts[expert_idx](token_x)
                token_out += weight * lora_delta
                
            final_output[i] = token_out.squeeze(0)
            
        # The base layer processing (e.g., standard FFN) happens outside this module.
        # This module returns the aggregated LoRA delta.
        return final_output.view(batch_size, seq_len, hidden_dim)
