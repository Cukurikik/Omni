import torch
import torch.nn as nn

# OMNI MOTHER: Drop-Upcycling (ICLR 2025)
# Training Sparse Mixture of Experts with Partial Re-initialization

class OmniDropUpcycling(nn.Module):
    def __init__(self, dense_model: nn.Module, num_experts: int, drop_rate: float = 0.5):
        super().__init__()
        self.num_experts = num_experts
        self.drop_rate = drop_rate
        
        # Base dense model weights
        self.dense_weights = dense_model.weight.data.clone()
        self.hidden_dim = self.dense_weights.size(-1)
        
        # Upcycled experts
        self.experts = nn.ModuleList([
            nn.Linear(self.hidden_dim, self.dense_weights.size(0)) 
            for _ in range(num_experts)
        ])
        
        self.router = nn.Linear(self.hidden_dim, num_experts)
        self._apply_partial_reinit()

    def _apply_partial_reinit(self):
        """Drops and re-initializes a fraction of the upcycled weights to break symmetry"""
        with torch.no_grad():
            for i, expert in enumerate(self.experts):
                # Copy dense weights first
                expert.weight.copy_(self.dense_weights)
                
                # Apply dropout mask for re-initialization
                mask = torch.rand_like(expert.weight) < self.drop_rate
                random_weights = torch.randn_like(expert.weight) * 0.02
                expert.weight[mask] = random_weights[mask]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Standard routing logic
        logits = self.router(x)
        probs = torch.softmax(logits, dim=-1)
        
        out = torch.zeros_like(x)
        for i, expert in enumerate(self.experts):
            out += expert(x) * probs[..., i:i+1]
        return out
