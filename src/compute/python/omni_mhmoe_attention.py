import torch
import torch.nn as nn

# OMNI MOTHER: MHMoE - Multi-Head Mixture-of-Experts
# Splits token representations into multiple heads, routing each head to different experts

class OmniMHMoEBlock(nn.Module):
    def __init__(self, hidden_dim: int, num_heads: int, num_experts: int):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        self.routers = nn.ModuleList([
            nn.Linear(self.head_dim, num_experts, bias=False) for _ in range(num_heads)
        ])
        
        # Each expert processes a head_dim
        self.experts = nn.ModuleList([
            nn.Sequential(nn.Linear(self.head_dim, self.head_dim * 4), nn.GELU(), nn.Linear(self.head_dim * 4, self.head_dim))
            for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, seq_len, dim = x.size()
        # [batch, seq, heads, head_dim]
        x_heads = x.view(batch, seq_len, self.num_heads, self.head_dim)
        
        out_heads = []
        for h in range(self.num_heads):
            h_input = x_heads[:, :, h, :]
            routing_weights = torch.softmax(self.routers[h](h_input), dim=-1)
            
            h_out = torch.zeros_like(h_input)
            for e, expert in enumerate(self.experts):
                h_out += routing_weights[:, :, e].unsqueeze(-1) * expert(h_input)
            out_heads.append(h_out)
            
        out = torch.cat(out_heads, dim=-1)
        return out
