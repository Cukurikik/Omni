import torch
import torch.nn as nn

# OMNI MOTHER: HyperNetworks for Dynamic MoE
# Generates weights for experts dynamically based on context

class OmniMoEHyperNetwork(nn.Module):
    def __init__(self, context_dim: int, expert_hidden_dim: int):
        super().__init__()
        self.expert_hidden_dim = expert_hidden_dim
        # Predicts weights for a linear layer
        self.weight_generator = nn.Linear(context_dim, expert_hidden_dim * expert_hidden_dim)
        self.bias_generator = nn.Linear(context_dim, expert_hidden_dim)

    def forward(self, context: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        # context: [batch, context_dim]
        # x: [batch, expert_hidden_dim]
        
        W = self.weight_generator(context).view(-1, self.expert_hidden_dim, self.expert_hidden_dim)
        b = self.bias_generator(context).unsqueeze(1)
        
        # Batched matrix multiplication
        out = torch.bmm(x.unsqueeze(1), W) + b
        return out.squeeze(1)
