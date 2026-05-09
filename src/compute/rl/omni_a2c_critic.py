"""
omni_a2c_critic.py — Advantage Actor-Critic (A2C) Value Network
Layer: Compute / Reinforcement Learning
Inspired by: openai/baselines (A2C)

Implements the Critic network for synchronous Advantage Actor-Critic.
The Critic learns the State-Value function V(s), which serves as a baseline
to compute the Advantage A(s, a) = Q(s, a) - V(s), significantly reducing
variance during policy gradient updates. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniA2CValueNetwork(nn.Module):
    def __init__(self, state_dim: int, hidden_dim: int = 64):
        """
        Calculates the expected cumulative reward from a given state.
        Architecture is typically smaller than the Actor in A2C.
        """
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(), # Tanh often preferred in A2C value networks for bounded gradients
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1) # Outputs a single scalar V(s)
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        state: (Batch, StateDim)
        Returns: (Batch, 1) Estimated value V(s)
        """
        return self.net(state)

def compute_advantages(rewards: torch.Tensor, 
                       values: torch.Tensor, 
                       dones: torch.Tensor, 
                       next_value: torch.Tensor, 
                       gamma: float = 0.99) -> torch.Tensor:
    """
    Computes standard N-step advantages.
    For GAE (Generalized Advantage Estimation), a lambda parameter would be added.
    """
    advantages = torch.zeros_like(rewards)
    returns = torch.zeros_like(rewards)
    
    # Calculate returns backwards
    R = next_value
    for t in reversed(range(len(rewards))):
        R = rewards[t] + gamma * R * (1.0 - dones[t])
        returns[t] = R
        
    advantages = returns - values.detach()
    
    # Normalize advantages for stability
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
    
    return advantages, returns

def update_critic(critic: OmniA2CValueNetwork, 
                  optimizer: torch.optim.Optimizer, 
                  states: torch.Tensor, 
                  returns: torch.Tensor) -> float:
    """
    Updates the value network using Mean Squared Error against the empirical returns.
    """
    predicted_values = critic(states)
    loss = F.mse_loss(predicted_values, returns)
    
    optimizer.zero_grad()
    loss.backward()
    nn.utils.clip_grad_norm_(critic.parameters(), max_norm=0.5)
    optimizer.step()
    
    return loss.item()
