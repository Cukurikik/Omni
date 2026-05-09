import torch
import torch.nn as nn

# OMNI MOTHER: InterMoE (Interaction Motion Generation)
# Routing joint/bone features to specialized interaction experts

class OmniInterMoE(nn.Module):
    def __init__(self, motion_dim: int, num_experts: int = 6):
        super().__init__()
        self.router = nn.Linear(motion_dim, num_experts)
        # Experts specialized in different motion types (walking, running, grabbing)
        self.experts = nn.ModuleList([
            nn.Linear(motion_dim, motion_dim) for _ in range(num_experts)
        ])

    def forward(self, motion_seq: torch.Tensor) -> torch.Tensor:
        # motion_seq: [batch, seq_len, motion_dim]
        logits = self.router(motion_seq)
        probs = torch.softmax(logits, dim=-1)
        
        out = torch.zeros_like(motion_seq)
        for i, expert in enumerate(self.experts):
            out += expert(motion_seq) * probs[..., i:i+1]
            
        return out
