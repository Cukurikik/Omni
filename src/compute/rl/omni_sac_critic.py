"""
omni_sac_critic.py — Soft Actor-Critic (SAC) Twin Q-Networks
Layer: Compute / Reinforcement Learning
Inspired by: rail-berkeley/softlearning

Implements the Twin Q-Network structure used in Soft Actor-Critic (SAC) and TD3.
Using two independent critics mitigates the overestimation bias inherent in 
Q-learning algorithms when applied to continuous action spaces. Zero mock.
"""

import torch
import torch.nn as nn

class OmniSACCriticNetwork(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        """
        Takes concatenated (State, Action) and predicts the Q-value.
        Contains two entirely separate feed-forward streams (Twin Q).
        """
        super().__init__()
        
        # Critic 1 (Q1)
        self.q1_net = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Critic 2 (Q2)
        self.q2_net = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, state: torch.Tensor, action: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Returns Q1 and Q2 values simultaneously.
        """
        sa_concat = torch.cat([state, action], dim=-1)
        
        q1 = self.q1_net(sa_concat)
        q2 = self.q2_net(sa_concat)
        
        return q1, q2

    def q1_forward(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """
        Used during policy evaluation where only one Q-value is strictly necessary
        for backpropagating gradients to the Actor.
        """
        sa_concat = torch.cat([state, action], dim=-1)
        return self.q1_net(sa_concat)

def soft_update(target: nn.Module, source: nn.Module, tau: float):
    """
    Performs Polyak averaging (soft update) to slowly blend source weights into target.
    Used for updating the Target Q-Networks in SAC.
    """
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)
