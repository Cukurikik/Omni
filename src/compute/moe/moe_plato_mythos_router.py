"""
moe_plato_mythos_router.py — Compute / Architecture
Layer: Compute / AI — PLATO-Native Recurrent-Depth Transformer

Inspired by the `plato-mythos` architecture, this module implements a recurrent-depth
Transformer where "rooms" act as MoE experts and "tiles" act as the KV cache.
It utilizes deadband halting to dynamically exit the recurrence loop when the 
expert activations stabilize (ACT - Adaptive Computation Time).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple

class PlatoMythosRouter(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, max_recurrence: int = 5, deadband_threshold: float = 0.01):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.max_recurrence = max_recurrence
        self.deadband_threshold = deadband_threshold
        
        # The routing gate that determines which "room" (expert) to visit next
        self.gate = nn.Linear(hidden_dim, num_experts)
        
        # ACT Halting mechanism: predicts the probability of stopping at current step
        self.halt_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        print(f"[Plato-Mythos] Initialized Recurrent-Depth Router (Max Steps: {max_recurrence}, Deadband: {deadband_threshold})")

    def forward(self, x: torch.Tensor, experts: nn.ModuleList) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (Batch, SeqLen, Dim)
        Executes a dynamic recurrent loop. Tokens bounce between experts until ACT halts them.
        """
        batch_size, seq_len, _ = x.shape
        device = x.device
        
        # Track accumulated state and halting probabilities
        accumulated_state = torch.zeros_like(x)
        accumulated_prob = torch.zeros(batch_size, seq_len, 1, device=device)
        remainder_prob = torch.ones(batch_size, seq_len, 1, device=device)
        
        # Tracking metrics for telemetry
        steps_taken = torch.zeros(batch_size, seq_len, 1, device=device)
        
        current_state = x
        
        for step in range(self.max_recurrence):
            # 1. Routing: Calculate expert assignment probabilities
            logits = self.gate(current_state)
            routing_weights = F.softmax(logits, dim=-1)
            
            # Top-1 Routing for recurrent step
            top_weight, top_idx = torch.topk(routing_weights, 1, dim=-1)
            
            # Execute selected expert (Vectorized/Mocked loop for production simplicity)
            # In a true sparse setup, this uses scatter/gather
            step_output = torch.zeros_like(current_state)
            for i, expert in enumerate(experts):
                expert_mask = (top_idx.squeeze(-1) == i)
                if expert_mask.any():
                    # Process only tokens assigned to this expert
                    valid_tokens = current_state[expert_mask]
                    out_tokens = expert(valid_tokens)
                    step_output[expert_mask] = out_tokens
            
            # 2. ACT Halting Probability
            halt_prob = self.halt_predictor(step_output)
            
            # 3. Deadband check: If halt_prob pushes accumulated_prob > 1 - deadband, we halt
            is_active = (accumulated_prob < (1.0 - self.deadband_threshold))
            
            # Calculate actual weight for this step
            step_weight = torch.where(
                accumulated_prob + halt_prob >= 1.0,
                remainder_prob, # Take exactly what's left
                halt_prob
            )
            
            # Apply update only to active tokens
            accumulated_state += torch.where(is_active, step_output * step_weight, torch.zeros_like(step_output))
            accumulated_prob += torch.where(is_active, step_weight, torch.zeros_like(step_weight))
            remainder_prob -= torch.where(is_active, step_weight, torch.zeros_like(step_weight))
            
            steps_taken += is_active.float()
            
            # Setup next state
            current_state = step_output
            
            # Early exit if all tokens have halted
            if not is_active.any():
                break
                
        # Add remainder if we hit max_recurrence before halting
        accumulated_state += current_state * remainder_prob
        
        return accumulated_state, steps_taken.mean()

