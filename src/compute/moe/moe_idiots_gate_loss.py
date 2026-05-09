# moe_idiots_gate_loss.py — Compute Layer: Idiots Gate Loss
# Calculates load balancing loss to prevent expert collapse in MoIE networks.

from typing import List

class LoadBalancingLoss:
    def __init__(self, num_experts: int, alpha: float = 0.01):
        self.num_experts = num_experts
        self.alpha = alpha
        
    def compute_loss(self, routing_probabilities: List[List[float]]) -> float:
        """
        Computes the auxiliary loss for MoE load balancing.
        routing_probabilities: [batch_size, num_experts]
        """
        batch_size = len(routing_probabilities)
        if batch_size == 0:
            return 0.0
            
        # Compute the mean probability routed to each expert across the batch
        expert_mean_probs = [0.0] * self.num_experts
        for probs in routing_probabilities:
            for i, p in enumerate(probs):
                expert_mean_probs[i] += p
                
        for i in range(self.num_experts):
            expert_mean_probs[i] /= batch_size
            
        # Coefficient of variation squared (CV^2)
        mean_of_means = sum(expert_mean_probs) / self.num_experts
        if mean_of_means == 0:
            return 0.0
            
        variance = sum((p - mean_of_means) ** 2 for p in expert_mean_probs) / self.num_experts
        cv_squared = variance / (mean_of_means ** 2)
        
        # Multiply by scaling factor alpha
        return self.alpha * cv_squared
