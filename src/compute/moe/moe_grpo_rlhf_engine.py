# moe_grpo_rlhf_engine.py — Compute
# Layer: Compute — Group Relative Policy Optimization (GRPO)
# Inspired by: LLM-Algorithm-Intern-Guide

import torch
import torch.nn as nn
from typing import List, Tuple

class GRPOEngine(nn.Module):
    """
    Implements GRPO (Group Relative Policy Optimization) for RLHF.
    Eliminates the need for a Critic model by normalizing rewards within a generated group.
    """
    def __init__(self, clip_epsilon: float = 0.2, kl_weight: float = 0.05):
        super().__init__()
        self.clip_epsilon = clip_epsilon
        self.kl_weight = kl_weight

    def forward(self, 
                policy_log_probs: torch.Tensor, 
                ref_log_probs: torch.Tensor, 
                rewards: torch.Tensor, 
                group_size: int) -> torch.Tensor:
        """
        rewards: [batch_size * group_size]
        policy_log_probs: [batch_size * group_size, seq_len]
        """
        batch_size = rewards.size(0) // group_size
        
        # Reshape to calculate group-relative advantages
        rewards_grouped = rewards.view(batch_size, group_size)
        
        # Mean and std across the group
        mean_rewards = rewards_grouped.mean(dim=1, keepdim=True)
        std_rewards = rewards_grouped.std(dim=1, keepdim=True) + 1e-8
        
        # Calculate Advantages (A_i)
        advantages = (rewards_grouped - mean_rewards) / std_rewards
        advantages = advantages.view(-1, 1) # [batch * group_size, 1]

        # Calculate Probability Ratio
        ratio = torch.exp(policy_log_probs - ref_log_probs)
        
        # Clipped Surrogate Objective
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1.0 - self.clip_epsilon, 1.0 + self.clip_epsilon) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()

        # KL Divergence Penalty
        kl_div = torch.exp(ref_log_probs - policy_log_probs) - (ref_log_probs - policy_log_probs) - 1
        kl_loss = kl_div.mean() * self.kl_weight

        total_loss = policy_loss + kl_loss
        return total_loss
