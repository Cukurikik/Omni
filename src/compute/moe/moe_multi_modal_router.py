"""
moe_multi_modal_router.py — Compute / Multimodal
Layer: Compute / AI — Multimodal MoE Router

Standard MoE routers only look at text embeddings. This router is designed for
Any-to-Any multimodal models. It explicitly identifies the modality of a token 
(Text, Image Patch, Audio Frame) and biases the routing toward experts specialized 
in that modality.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from enum import Enum

class Modality(Enum):
    TEXT = 0
    IMAGE = 1
    AUDIO = 2

class MultiModalRouter(nn.Module):
    """
    Routes tokens not just by semantic content, but by their core modality.
    """
    def __init__(self, hidden_dim: int, num_experts: int):
        super().__init__()
        self.num_experts = num_experts
        
        # The core routing network
        self.gate = nn.Linear(hidden_dim, num_experts)
        
        # Modality bias: We learn a bias vector for each modality
        # This nudges vision tokens to vision experts without hardcoding the split
        self.modality_bias = nn.Parameter(torch.randn(3, num_experts) * 0.1)

    def forward(self, embeddings: torch.Tensor, modality_ids: torch.Tensor) -> torch.Tensor:
        """
        embeddings: (Batch * SeqLen, hidden_dim)
        modality_ids: (Batch * SeqLen) containing Modality Enum values
        """
        # Base routing logits
        logits = self.gate(embeddings) # (N, num_experts)
        
        # Look up the bias for the corresponding modality of each token
        # modality_ids should be an integer tensor (0, 1, or 2)
        bias = self.modality_bias[modality_ids] # (N, num_experts)
        
        # Apply the learned bias
        logits = logits + bias
        
        # Standard Softmax
        routing_weights = F.softmax(logits, dim=-1)
        
        return routing_weights

# Example showing structural usage
# router = MultiModalRouter(hidden_dim=256, num_experts=8)
# emb = torch.randn(5, 256)
# mods = torch.tensor([Modality.TEXT.value, Modality.IMAGE.value, Modality.IMAGE.value, Modality.AUDIO.value, Modality.TEXT.value])
# probs = router(emb, mods)
