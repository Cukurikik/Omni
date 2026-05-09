import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER: Grok-1 Style MoE Utilities
# Implements advanced load balancing and expert tracking for massive 300B+ models

class OmniGrokMoEUtils:
    @staticmethod
    def calculate_auxiliary_loss(gate_logits: torch.Tensor, top_indices: torch.Tensor, num_experts: int) -> torch.Tensor:
        """
        Compute the load balancing loss.
        gate_logits: [batch_size * seq_len, num_experts]
        top_indices: [batch_size * seq_len, top_k]
        """
        num_tokens = gate_logits.shape[0]
        
        # 1. Compute expert routing probabilities (Importance)
        probs = F.softmax(gate_logits, dim=-1) # [N, E]
        expert_importance = probs.mean(dim=0)  # [E]
        
        # 2. Compute actual fraction of tokens assigned to each expert (Load)
        # Create one-hot mask for assigned experts
        # top_indices: [N, K]
        mask = F.one_hot(top_indices, num_classes=num_experts).float() # [N, K, E]
        mask = mask.sum(dim=1) # [N, E]
        
        expert_load = mask.mean(dim=0) # [E]
        
        # 3. Compute loss: sum(importance * load) * num_experts
        # This penalizes both skewed importance (some experts are highly preferred)
        # and skewed load (some experts get all the tokens).
        aux_loss = torch.sum(expert_importance * expert_load) * num_experts
        
        return aux_loss

class OmniGrokRouter(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        # Grok uses bias=False for gate
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)
        
    def forward(self, x: torch.Tensor):
        logits = self.gate(x)
        
        # Jitter routing for training stability (z-loss not included here for simplicity, but could be added)
        if self.training:
            # Add uniform noise [-0.01, 0.01]
            noise = torch.empty_like(logits).uniform_(-0.01, 0.01)
            logits = logits + noise
            
        routing_weights = F.softmax(logits, dim=-1)
        
        topk_weights, topk_indices = torch.topk(routing_weights, self.top_k, dim=-1)
        
        # Renormalize
        topk_weights = topk_weights / topk_weights.sum(dim=-1, keepdim=True)
        
        aux_loss = OmniGrokMoEUtils.calculate_auxiliary_loss(logits, topk_indices, self.num_experts)
        
        return topk_weights, topk_indices, aux_loss
