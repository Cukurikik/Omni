import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, Optional

# OMNI RL: DQN Agent
# Python PyTorch implementation of Deep Q-Network for Reinforcement Learning.
# Source: rlcode/reinforcement-learning

class DQNError(Exception):
    pass

class QNetwork(nn.Module):
    def __init__(self, state_size: int, action_size: int):
        super().__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)
        self.relu = nn.ReLU()

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.fc1(state))
        x = self.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size: int, action_size: int, lr: float = 0.001, gamma: float = 0.99):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        
        self.policy_net = QNetwork(state_size, action_size)
        self.target_net = QNetwork(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

    def train_step(self, states: torch.Tensor, actions: torch.Tensor, rewards: torch.Tensor, next_states: torch.Tensor, dones: torch.Tensor) -> Tuple[Optional[float], Optional[DQNError]]:
        """
        Executes a single Q-learning training step.
        Monadic return type enforces error checking.
        """
        try:
            # Predict Q values for current states
            q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
            
            # Predict next Q values from target network
            with torch.no_grad():
                max_next_q_values = self.target_net(next_states).max(1)[0]
                target_q_values = rewards + (self.gamma * max_next_q_values * (1 - dones))

            # Compute loss
            loss = self.criterion(q_values, target_q_values)
            
            # Optimize
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
            self.optimizer.step()
            
            return loss.item(), None
            
        except Exception as e:
            return None, DQNError(f"DQN Training Step Failed: {str(e)}")

    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
