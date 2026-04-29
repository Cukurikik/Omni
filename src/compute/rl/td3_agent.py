import torch
import torch.nn as nn

class TD3Agent(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
            nn.Tanh()
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        try:
            return self.actor(state)
        except Exception as e:
            raise RuntimeError(f"TD3 actor failed: {e}")
