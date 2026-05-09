import torch
import torch.nn as nn

# OMNI MOTHER: T2MIR - Mixture-of-Experts Meets In-Context Reinforcement Learning
# Uses MoE architectures to dynamically load policies based on trajectory contexts

class OmniT2MIRAgent(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, num_experts: int):
        super().__init__()
        self.context_encoder = nn.Linear(state_dim + action_dim, 128)
        self.router = nn.Linear(128, num_experts)
        self.experts = nn.ModuleList([
            nn.Sequential(nn.Linear(state_dim, 64), nn.ReLU(), nn.Linear(64, action_dim))
            for _ in range(num_experts)
        ])

    def forward(self, state: torch.Tensor, context_trajectory: torch.Tensor):
        # context_trajectory: [batch, seq, state_dim + action_dim]
        ctx_emb = self.context_encoder(context_trajectory).mean(dim=1) # pooling
        route_weights = torch.softmax(self.router(ctx_emb), dim=-1)
        
        action_output = torch.zeros((state.size(0), self.experts[0][2].out_features), device=state.device)
        for i, expert in enumerate(self.experts):
            action_output += route_weights[:, i].unsqueeze(-1) * expert(state)
            
        return action_output
