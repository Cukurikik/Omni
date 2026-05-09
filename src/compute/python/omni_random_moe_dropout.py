import torch
import torch.nn as nn
import random

# OMNI MOTHER: Sparse MoE as the New Dropout (ICLR 2023)
# Randomly drops experts to scale dense and self-slimmable Transformers

class OmniRandomMoEDropout(nn.Module):
    def __init__(self, num_experts: int, dropout_rate: float = 0.1):
        super().__init__()
        self.num_experts = num_experts
        self.dropout_rate = dropout_rate

    def forward(self, routing_logits: torch.Tensor, training: bool = True) -> torch.Tensor:
        # routing_logits: [batch, seq, num_experts]
        if not training or self.dropout_rate == 0.0:
            return routing_logits
            
        # Create dropout mask
        mask = torch.rand_like(routing_logits) > self.dropout_rate
        
        # Mask out logits (set to very negative value)
        dropped_logits = routing_logits.masked_fill(~mask, float('-inf'))
        
        return dropped_logits
