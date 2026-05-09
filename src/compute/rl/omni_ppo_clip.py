"""
omni_ppo_clip.py — Proximal Policy Optimization (PPO) Clipped Objective
Layer: Compute / Reinforcement Learning
Inspired by: openai/baselines

Implements the core surrogate objective function of PPO. Prevents destructively 
large policy updates by clipping the probability ratio between the new and old 
policies. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniPPOObjective(nn.Module):
    def __init__(self, clip_ratio: float = 0.2, c1: float = 1.0, c2: float = 0.01):
        """
        clip_ratio: Epsilon for clipping (usually 0.2)
        c1: Value loss coefficient
        c2: Entropy bonus coefficient (encourages exploration)
        """
        super().__init__()
        self.clip_ratio = clip_ratio
        self.c1 = c1
        self.c2 = c2

    def forward(
        self, 
        action_probs: torch.Tensor, 
        old_action_probs: torch.Tensor, 
        advantages: torch.Tensor, 
        state_values: torch.Tensor, 
        rewards: torch.Tensor, 
        action_entropy: torch.Tensor
    ) -> torch.Tensor:
        """
        action_probs: Probabilities of the taken actions under the CURRENT policy (Batch,)
        old_action_probs: Probabilities of the taken actions under the OLD policy (Batch,)
        advantages: A_t (Batch,)
        state_values: V(s_t) predicted by the critic (Batch,)
        rewards: Actual discounted returns (Batch,)
        action_entropy: Entropy of the current policy's action distribution (Batch,)
        
        Returns a single scalar loss (to be MINIMIZED, so we return the negative of the objective).
        """
        # 1. Calculate the probability ratio r_t(theta)
        # Adding epsilon to prevent division by zero
        ratios = action_probs / (old_action_probs + 1e-8)

        # 2. Calculate the surrogate objective parts
        surr1 = ratios * advantages
        
        # clamp ratio between [1 - epsilon, 1 + epsilon]
        clipped_ratios = torch.clamp(ratios, 1.0 - self.clip_ratio, 1.0 + self.clip_ratio)
        surr2 = clipped_ratios * advantages

        # L^{CLIP} = E [ min(r_t * A_t, clip(r_t, 1-e, 1+e) * A_t) ]
        # We want to MAXIMIZE this, so in PyTorch we MINIMIZE the negative
        policy_loss = -torch.min(surr1, surr2).mean()

        # 3. Value Loss: L^{VF} = (V(s_t) - V_target)^2
        value_loss = F.mse_loss(state_values, rewards)

        # 4. Entropy Bonus (encourages exploration, we want to MAXIMIZE entropy, so MINIMIZE negative)
        entropy_loss = -action_entropy.mean()

        # Final PPO Loss
        total_loss = policy_loss + self.c1 * value_loss + self.c2 * entropy_loss
        
        return total_loss
