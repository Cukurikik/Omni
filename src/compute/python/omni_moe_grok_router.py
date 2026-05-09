import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniMoEGrokRouter(nn.Module):
    """
    OMNI Framework - Grok-inspired Sparse Router
    Implements a jittered, sparse routing mechanism to prevent token dropping 
    and encourage uniform expert utilization, similar to Grok-1 architecture.
    Features auxiliary load-balancing loss computation.
    """
    def __init__(self, d_model: int, num_experts: int, top_k: int = 2, jitter_eps: float = 0.01):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.jitter_eps = jitter_eps
        
        # Routing linear layer
        self.w_gate = nn.Linear(d_model, num_experts, bias=False)
        
    def forward(self, hidden_states: torch.Tensor, training: bool = True):
        # hidden_states: [batch_size, seq_len, d_model]
        batch_size, seq_len, _ = hidden_states.shape
        flat_hidden = hidden_states.view(-1, hidden_states.size(-1))
        
        # Apply routing jitter during training for exploration
        if training and self.jitter_eps > 0:
            jitter = torch.empty_like(flat_hidden).uniform_(-self.jitter_eps, self.jitter_eps)
            flat_hidden = flat_hidden * (1.0 + jitter)
            
        # Compute routing logits [total_tokens, num_experts]
        logits = self.w_gate(flat_hidden)
        
        # Compute softmax probabilities
        routing_probs = F.softmax(logits, dim=-1)
        
        # Select Top-K experts
        topk_probs, topk_indices = torch.topk(routing_probs, self.top_k, dim=-1)
        
        # Normalize Top-K probabilities (so they sum to 1.0 for each token)
        topk_probs = topk_probs / topk_probs.sum(dim=-1, keepdim=True)
        
        # Compute Load Balancing Loss
        # 1. Fraction of tokens routed to each expert
        expert_mask = F.one_hot(topk_indices, num_classes=self.num_experts).float()
        tokens_per_expert = expert_mask.sum(dim=0).sum(dim=0) / (batch_size * seq_len * self.top_k)
        
        # 2. Average probability assigned to each expert across all tokens
        avg_prob_per_expert = routing_probs.mean(dim=0)
        
        # 3. Auxiliary loss: N * sum(f_i * P_i)
        load_balancing_loss = self.num_experts * torch.sum(tokens_per_expert * avg_prob_per_expert)
        
        return topk_probs, topk_indices, load_balancing_loss

# Testing the router
if __name__ == "__main__":
    router = OmniMoEGrokRouter(d_model=1024, num_experts=8, top_k=2)
    x = torch.randn(4, 128, 1024) # Batch 4, Seq 128
    probs, indices, loss = router(x)
    print(f"OMNI Python: Grok Router execution successful. Aux Loss: {loss.item():.4f}")
