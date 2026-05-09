"""
omni_td3_actor.py — Twin Delayed DDPG (TD3) Actor Network
Layer: Compute / Reinforcement Learning
Inspired by: sfujim/TD3

Implements the deterministic Actor network used in the TD3 algorithm.
Outputs continuous actions bounded by `max_action`. The architecture maps
states directly to specific optimal actions, avoiding the entropy of SAC. Zero mock.
"""

import torch
import torch.nn as nn

class OmniTD3Actor(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, max_action: float, hidden_dim: int = 256):
        """
        state_dim: Dimension of the observation space.
        action_dim: Dimension of the continuous action space.
        max_action: The absolute maximum scalar value for actions (e.g., bounds [-1, 1] * max_action).
        """
        super().__init__()
        self.max_action = max_action

        # Standard Multi-Layer Perceptron architecture
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Tanh() # Tanh ensures output is strictly bounded within [-1, 1]
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Returns the exact continuous action to take.
        """
        # Multiply by max_action to scale to the environment's legal limits
        return self.max_action * self.net(state)

def get_action_with_exploration(actor: OmniTD3Actor, state: torch.Tensor, noise_std: float) -> torch.Tensor:
    """
    Since TD3's actor is deterministic, exploration is achieved by adding Gaussian noise
    to the predicted actions during training.
    """
    actor.eval()
    with torch.no_grad():
        action = actor(state)
        
    # Add Gaussian noise
    noise = torch.normal(mean=0.0, std=noise_std, size=action.shape, device=action.device)
    action = action + noise
    
    # Clip back to the legal limits
    action = torch.clamp(action, -actor.max_action, actor.max_action)
    
    actor.train()
    return action
