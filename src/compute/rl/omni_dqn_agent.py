"""
omni_dqn_agent.py — Deep Q-Network (DQN)
Layer: Compute / AI

Implements a Deep Q-Network agent featuring Experience Replay and a Target Network
to stabilize learning in discrete action spaces. Zero-mock.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import numpy as np

class OmniQNet(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class OmniReplayBuffer:
    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)

class OmniDQNAgent:
    def __init__(self, state_dim: int, action_dim: int, lr: float = 1e-3, 
                 gamma: float = 0.99, batch_size: int = 64, capacity: int = 10000):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size

        self.q_net = OmniQNet(state_dim, action_dim)
        self.target_net = OmniQNet(state_dim, action_dim)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)
        self.memory = OmniReplayBuffer(capacity)
        self.loss_fn = nn.MSELoss()

        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

    def select_action(self, state: np.ndarray, evaluate: bool = False) -> int:
        if not evaluate and random.random() < self.epsilon:
            return random.randrange(self.action_dim)
            
        with torch.no_grad():
            state_t = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_net(state_t)
            return q_values.argmax().item()

    def store_transition(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)

    def update(self):
        if len(self.memory) < self.batch_size:
            return

        state, action, reward, next_state, done = self.memory.sample(self.batch_size)

        state_t = torch.FloatTensor(state)
        action_t = torch.LongTensor(action).unsqueeze(1)
        reward_t = torch.FloatTensor(reward).unsqueeze(1)
        next_state_t = torch.FloatTensor(next_state)
        done_t = torch.FloatTensor(done).unsqueeze(1)

        # Compute current Q values
        q_values = self.q_net(state_t).gather(1, action_t)

        # Compute target Q values
        with torch.no_grad():
            max_next_q = self.target_net(next_state_t).max(1)[0].unsqueeze(1)
            target_q_values = reward_t + self.gamma * max_next_q * (1 - done_t)

        loss = self.loss_fn(q_values, target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        nn.utils.clip_grad_norm_(self.q_net.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_target_network(self):
        self.target_net.load_state_dict(self.q_net.state_dict())
