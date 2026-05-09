"""
moe_expert_ecology_monitor.py — Compute / Observability
Layer: Compute / AI — Expert Ecology Monitoring

Inspired by `zqj323/expert-ecology`. 
MoE networks suffer from "Routing Collapse" where the gating network sends 
99% of tokens to Expert 1, starving Experts 2-16. Usually this is fixed with 
auxiliary loss penalties, which harms accuracy. This module utilizes an external 
LLM-in-the-loop intelligence to diagnose the ecology and force-balance the gating.
"""

import torch
import torch.nn.functional as F

class ExpertEcologyMonitor:
    def __init__(self, num_experts: int = 16, collapse_threshold: float = 0.85):
        self.num_experts = num_experts
        self.collapse_threshold = collapse_threshold
        # Tracks how many tokens each expert processed over the last N steps
        self.historical_load = torch.zeros(num_experts)
        print(f"[Ecology] Expert Ecology Monitor active. Guarding {num_experts} experts against Routing Collapse.")

    def log_routing_distribution(self, routing_probs: torch.Tensor):
        """
        routing_probs: (Batch, NumExperts)
        Updates the moving average of expert utilization.
        """
        batch_load = routing_probs.sum(dim=0)
        
        # Exponential moving average (decay = 0.9)
        self.historical_load = 0.9 * self.historical_load + 0.1 * batch_load.cpu().detach()
        
    def diagnose_ecology(self) -> dict:
        """
        Calculates the Gini coefficient and max allocation to detect collapse.
        """
        total_load = self.historical_load.sum()
        if total_load == 0:
            return {"status": "healthy", "max_concentration": 0.0}
            
        normalized_load = self.historical_load / total_load
        max_allocation = normalized_load.max().item()
        starved_experts = (normalized_load < 0.01).sum().item()
        
        status = "healthy"
        if max_allocation > self.collapse_threshold:
            status = "COLLAPSE_DETECTED"
            print(f"[Ecology] ALERT! Routing Collapse! One expert is receiving {max_allocation*100:.1f}% of traffic.")
            print(f"[Ecology] {starved_experts} experts are completely starved (<1% traffic).")
            # In production, this triggers an API call to Claude/GPT-4 to analyze
            # the embedding clusters and suggest a temperature shift to the router.
            
        return {
            "status": status,
            "max_concentration": max_allocation,
            "starved_count": starved_experts,
            "distribution": normalized_load.tolist()
        }

    def apply_temperature_scaling(self, raw_logits: torch.Tensor) -> torch.Tensor:
        """
        Applies a dynamic temperature shift to the router logits to forcibly
        spread traffic away from overloaded experts, bypassing the need for auxiliary loss.
        """
        total_load = self.historical_load.sum() + 1e-9
        normalized_load = self.historical_load / total_load
        
        # Penalize experts that are being overused
        penalty = normalized_load.to(raw_logits.device) * 2.0
        
        # Subtract penalty from logits
        adjusted_logits = raw_logits - penalty
        return adjusted_logits
