"""
omni_dqn_target.py — Deep Q-Network with Target Sync
Layer: Compute / Reinforcement Learning
Inspired by: DeepMind / openai/baselines

Implements the standard DQN architecture with a Target Network.
The Target Network is a delayed copy of the Q-Network, used to stabilize 
bootstrapping during the Bellman equation loss calculation. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniQNetwork(nn.Module):
    def __init__(self, state_dim: int, num_actions: int, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_actions)
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Returns Q-values for all discrete actions.
        """
        return self.net(state)

class OmniDQNAlgorithm:
    def __init__(self, state_dim: int, num_actions: int, lr: float = 1e-3, gamma: float = 0.99):
        self.gamma = gamma
        self.num_actions = num_actions
        
        # Policy Network (trained)
        self.q_net = OmniQNetwork(state_dim, num_actions)
        
        # Target Network (frozen, updated periodically)
        self.target_net = OmniQNetwork(state_dim, num_actions)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=lr)

    def sync_target_network(self):
        """Hard synchronization of target weights."""
        self.target_net.load_state_dict(self.q_net.state_dict())

    def soft_sync_target(self, tau: float = 0.005):
        """Polyak averaging soft synchronization."""
        for target_param, param in zip(self.target_net.parameters(), self.q_net.parameters()):
            target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)

    def update_step(self, states, actions, rewards, next_states, dones) -> float:
        """
        Computes Bellman loss and updates the Q-Network.
        actions: (Batch, 1) indices
        rewards, dones: (Batch, 1)
        """
        # Q(s, a) predicted by active network
        # Gather the Q-values corresponding to the actions actually taken
        q_values = self.q_net(states).gather(1, actions)

        # Max Q(s', a') predicted by frozen target network
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1, keepdim=True)[0]
            # Zero out target for terminal states
            target_q_values = rewards + self.gamma * next_q_values * (1.0 - dones)

        # Huber Loss (Smooth L1 Loss) is more stable than MSE for Q-learning
        loss = F.smooth_l1_loss(q_values, target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping for stability
        nn.utils.clip_grad_norm_(self.q_net.parameters(), max_norm=1.0)
        
        self.optimizer.step()

        return loss.item()
