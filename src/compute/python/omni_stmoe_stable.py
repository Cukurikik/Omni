import torch
import torch.nn as nn
import torch.nn.functional as F

# OMNI MOTHER: ST-MoE (Stable and Transferable Mixture-of-Experts)
# Addresses training instability in sparse MoE models using Router Z-Loss

class OmniSTMoERouter(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, z_loss_coef: float = 1e-3):
        super().__init__()
        self.num_experts = num_experts
        self.z_loss_coef = z_loss_coef
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)
        
    def forward(self, x: torch.Tensor):
        logits = self.gate(x)
        
        # 1. Z-Loss for stability
        # Penalizes large logits to prevent softmax saturation and rounding errors in fp16/bf16
        log_z = torch.logsumexp(logits, dim=-1)
        z_loss = self.z_loss_coef * torch.mean(log_z ** 2)
        
        # 2. Routing probabilities
        routing_weights = F.softmax(logits, dim=-1)
        
        # Top-1 selection (ST-MoE often uses Top-1 with high capacity factor)
        top1_weight, top1_indices = torch.max(routing_weights, dim=-1, keepdim=True)
        
        # 3. Capacity scaling and Token Dropping (Simulated)
        # In ST-MoE, token dropping is severe if capacity is exceeded.
        # Here we return the structures needed for the caller to drop tokens.
        
        return top1_weight, top1_indices, routing_weights, z_loss

class OmniSTMoEBlock(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int):
        super().__init__()
        self.router = OmniSTMoERouter(hidden_dim, num_experts)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim * 4),
                nn.GELU(),
                nn.Linear(hidden_dim * 4, hidden_dim)
            ) for _ in range(num_experts)
        ])
        
    def forward(self, x: torch.Tensor):
        B, S, D = x.shape
        x_flat = x.view(-1, D)
        
        top1_weight, top1_indices, full_probs, z_loss = self.router(x_flat)
        
        out_flat = torch.zeros_like(x_flat)
        top1_indices = top1_indices.squeeze(-1)
        
        for i, expert in enumerate(self.experts):
            mask = (top1_indices == i)
            if mask.any():
                expert_in = x_flat[mask]
                # Multiply by routing weight *before* the expert (a design choice sometimes used)
                # or *after*. ST-MoE usually multiplies after.
                expert_out = expert(expert_in)
                out_flat[mask] = expert_out * top1_weight[mask]
                
        return out_flat.view(B, S, D), z_loss
