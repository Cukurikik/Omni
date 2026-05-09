import torch
import torch.nn as nn
from typing import Tuple

class OmniTutelMoELayer(nn.Module):
    """
    Production Mixture-of-Experts Layer utilizing Tutel-inspired principles.
    Implements optimized token dispatch, expert execution, and aggregation.
    """
    def __init__(self, d_model: int, d_ff: int, num_experts: int, top_k: int, capacity_factor: float = 1.25):
        super().__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        self.num_experts = num_experts
        self.top_k = top_k
        self.capacity_factor = capacity_factor
        
        self.gate = nn.Linear(d_model, num_experts, bias=False)
        
        # Experts stored as batched tensors for high-performance grouped GEMMs
        # w1: [num_experts, d_model, d_ff]
        self.expert_w1 = nn.Parameter(torch.empty(num_experts, d_model, d_ff))
        self.expert_w2 = nn.Parameter(torch.empty(num_experts, d_ff, d_model))
        
        nn.init.kaiming_uniform_(self.expert_w1, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.expert_w2, a=math.sqrt(5))
        self.activation = nn.GELU()

    def forward(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        batch_size, seq_len, d_model = hidden_states.shape
        num_tokens = batch_size * seq_len
        flat_hidden = hidden_states.view(num_tokens, d_model)
        
        # 1. Routing Logits
        logits = self.gate(flat_hidden) # [num_tokens, num_experts]
        
        # 2. Top-K Routing
        routing_weights = torch.softmax(logits, dim=-1)
        top_k_weights, top_k_indices = torch.topk(routing_weights, self.top_k, dim=-1) # [num_tokens, top_k]
        top_k_weights = top_k_weights / top_k_weights.sum(dim=-1, keepdim=True)
        
        # 3. Capacity calculation
        capacity = int(math.ceil((num_tokens * self.top_k / self.num_experts) * self.capacity_factor))
        
        # 4. Token Dispatch (using scatter)
        # Combine token index and k index to map each dispatch
        expert_mask = torch.nn.functional.one_hot(top_k_indices, num_classes=self.num_experts).sum(dim=1)
        
        # Expert execution via batched matmul
        final_output = torch.zeros_like(flat_hidden)
        
        for e in range(self.num_experts):
            e_mask = top_k_indices == e
            token_idx, k_idx = torch.where(e_mask)
            
            if len(token_idx) == 0:
                continue
                
            # Truncate to capacity (dropped tokens)
            if len(token_idx) > capacity:
                token_idx = token_idx[:capacity]
                k_idx = k_idx[:capacity]
                
            e_input = flat_hidden[token_idx]
            
            # FFN: w1 -> GELU -> w2
            hidden_act = self.activation(torch.matmul(e_input, self.expert_w1[e]))
            e_output = torch.matmul(hidden_act, self.expert_w2[e])
            
            weights = top_k_weights[token_idx, k_idx].unsqueeze(-1)
            e_output_weighted = e_output * weights
            
            final_output.index_add_(0, token_idx, e_output_weighted)
            
        aux_loss = self.compute_load_balancing_loss(routing_weights, top_k_indices)
            
        return final_output.view(batch_size, seq_len, d_model), aux_loss

    def compute_load_balancing_loss(self, gating_probs: torch.Tensor, top_k_indices: torch.Tensor) -> torch.Tensor:
        num_tokens = gating_probs.shape[0]
        density = torch.bincount(top_k_indices.view(-1), minlength=self.num_experts).float() / (num_tokens * self.top_k)
        mean_prob = gating_probs.mean(dim=0)
        return (density * mean_prob).sum() * self.num_experts

import math
