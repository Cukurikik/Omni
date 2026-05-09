import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniPhi3MiniMoE(nn.Module):
    """
    OMNI Framework - Phi-3 Mini MoE
    A highly optimized, small-scale Mixture of Experts architecture designed 
    to run locally on edge devices (phones, laptops).
    Uses heavy parameter sharing and aggressive pruning (Top-1 routing).
    Inspired by Microsoft Phi-3-Mini design principles adapted for MoE.
    """
    def __init__(self, d_model: int = 3072, num_experts: int = 4):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        
        # Lightweight router
        self.router = nn.Linear(d_model, num_experts, bias=False)
        
        # Shared projection in for all experts (reduces memory footprint)
        self.shared_gate_up = nn.Linear(d_model, d_model * 2, bias=False)
        
        # Expert-specific down projections
        self.expert_down_projs = nn.ModuleList([
            nn.Linear(d_model, d_model, bias=False) for _ in range(num_experts)
        ])
        
        print(f"OMNI Python: Initialized Edge-optimized Phi-3-Mini MoE with {num_experts} experts. Top-1 Routing active.")

    def forward(self, hidden_states: torch.Tensor):
        # hidden_states: [B, S, D]
        batch_size, seq_len, _ = hidden_states.shape
        flat_hidden = hidden_states.view(-1, self.d_model)
        
        # Top-1 Routing for extreme efficiency on edge devices
        router_logits = self.router(flat_hidden)
        routing_weights, selected_experts = torch.max(F.softmax(router_logits, dim=-1), dim=-1)
        
        # Pre-compute the shared SiLU-Gated projection
        gate_up_proj = self.shared_gate_up(flat_hidden)
        gate, up = gate_up_proj.chunk(2, dim=-1)
        activated_hidden = F.silu(gate) * up
        
        output_hidden = torch.zeros_like(flat_hidden)
        
        # Dispatch to specific experts
        for i, down_proj in enumerate(self.expert_down_projs):
            expert_mask = (selected_experts == i)
            if expert_mask.any():
                # Extract tokens for this expert
                expert_tokens = activated_hidden[expert_mask]
                # Apply expert-specific down projection
                expert_out = down_proj(expert_tokens)
                # Multiply by router probability and scatter back
                output_hidden[expert_mask] = expert_out * routing_weights[expert_mask].unsqueeze(-1)
                
        return output_hidden.view(batch_size, seq_len, self.d_model)

# test
# model = OmniPhi3MiniMoE()
# out = model(torch.randn(1, 128, 3072))
