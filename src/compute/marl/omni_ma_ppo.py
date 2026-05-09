"""
omni_ma_ppo.py — Multi-Agent PPO
Inspired by: MAPPO algorithms in modern RL frameworks
Layer: Compute / AI

Centralized Critic, Decentralized Actor (CTDE) Proximal Policy Optimization
for coordinating swarms of autonomous agents within the Locoformer engine.
"""

import torch
import torch.nn as nn
from typing import List, Tuple

class OmniActor(nn.Module):
    """Decentralized actor policy taking only local observation."""
    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.action_head = nn.Linear(hidden_dim, action_dim)
        # Log standard deviation for continuous action space
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(self, local_obs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.net(local_obs)
        mean = self.action_head(features)
        return mean, self.log_std

class OmniCentralizedCritic(nn.Module):
    """Centralized critic taking global state (all observations)."""
    def __init__(self, global_state_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(global_state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, global_state: torch.Tensor) -> torch.Tensor:
        return self.net(global_state)

class MAPPOAgentGroup:
    """Orchestrates MAPPO updates."""
    def __init__(self, num_agents: int, obs_dim: int, action_dim: int):
        self.num_agents = num_agents
        # CTDE Setup
        self.actor = OmniActor(obs_dim, action_dim)
        self.critic = OmniCentralizedCritic(num_agents * obs_dim)
        
    def act(self, local_obs_list: torch.Tensor) -> torch.Tensor:
        """
        local_obs_list: (NumAgents, ObsDim)
        """
        with torch.no_grad():
            means, log_std = self.actor(local_obs_list)
            stds = log_std.exp().expand_as(means)
            dist = torch.distributions.Normal(means, stds)
            actions = dist.sample()
        return actions

    def evaluate_global_state(self, global_state: torch.Tensor) -> torch.Tensor:
        """
        global_state: (Batch, NumAgents * ObsDim)
        Returns Value: (Batch, 1)
        """
        return self.critic(global_state)
