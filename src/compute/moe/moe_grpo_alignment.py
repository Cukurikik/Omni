"""
moe_grpo_alignment.py — Compute / Training
Layer: Compute / AI — Group Relative Policy Optimization (GRPO)

Inspired by `AarambhDevHub/APEX-1`.
Unlike standard PPO which requires a massive external Critic model (consuming 
double the VRAM), GRPO is an actor-only RLHF method. It generates multiple 
outputs from the same prompt and normalizes the rewards within the group to 
derive an advantage score. Critical for fine-tuning massive MoE networks.
"""

import torch
import torch.nn as nn
from typing import List, Callable

class GRPOAligner:
    def __init__(self, moe_model: nn.Module, kl_coeff: float = 0.05, clip_range: float = 0.2):
        self.model = moe_model
        self.kl_coeff = kl_coeff
        self.clip_range = clip_range
        print("[GRPO] Initialized Group Relative Policy Optimization (Actor-Only RLHF).")

    def compute_loss(
        self, 
        prompts: torch.Tensor, 
        old_logprobs: torch.Tensor,
        action_logprobs: torch.Tensor, 
        ref_logprobs: torch.Tensor, 
        rewards: torch.Tensor, 
        group_size: int = 4
    ) -> torch.Tensor:
        """
        Calculates the GRPO loss for a batch of generated trajectories.
        rewards: (Batch_size,) where Batch_size is a multiple of group_size
        """
        batch_size = rewards.size(0)
        assert batch_size % group_size == 0, "Batch size must be a multiple of group_size."

        # 1. Group-Relative Advantage Calculation
        # Reshape rewards to (Num_Groups, Group_Size)
        grouped_rewards = rewards.view(-1, group_size)
        
        # Calculate mean and std within each group
        group_mean = grouped_rewards.mean(dim=1, keepdim=True)
        group_std = grouped_rewards.std(dim=1, keepdim=True) + 1e-8
        
        # Normalize rewards to get Advantages
        advantages = (grouped_rewards - group_mean) / group_std
        advantages = advantages.view(-1) # Flatten back to (Batch_size,)

        # 2. Probability Ratio (New Policy / Old Policy)
        ratio = torch.exp(action_logprobs - old_logprobs)

        # 3. Clipped Surrogate Objective
        unclipped_loss = ratio * advantages
        clipped_loss = torch.clamp(ratio, 1.0 - self.clip_range, 1.0 + self.clip_range) * advantages
        
        # Maximize the minimum of clipped and unclipped
        policy_loss = -torch.min(unclipped_loss, clipped_loss).mean()

        # 4. KL Divergence Penalty (Keep policy close to reference model)
        # Using exact KL: log(p) - log(q)
        kl_div = action_logprobs - ref_logprobs
        kl_penalty = self.kl_coeff * kl_div.mean()

        total_loss = policy_loss + kl_penalty
        
        return total_loss

# Usage Example:
# aligner = GRPOAligner(moe_model)
# loss = aligner.compute_loss(prompts, old_lp, new_lp, ref_lp, rewards=torch.tensor([1.0, 0.5, -0.5, 2.0]))
# loss.backward()
