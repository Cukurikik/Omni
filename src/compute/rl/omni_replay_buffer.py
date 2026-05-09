"""
omni_replay_buffer.py — Experience Replay Buffer
Layer: Compute / Reinforcement Learning
Inspired by: openai/baselines

Implements a cyclic replay buffer for off-policy Reinforcement Learning algorithms
(like DQN or SAC). Stores transitions (s, a, r, s', done) and samples them uniformly
to break temporal correlations during neural network training. Zero mock.
"""

import numpy as np
import torch

class OmniReplayBuffer:
    def __init__(self, capacity: int, state_dim: int, action_dim: int, device: torch.device = None):
        self.capacity = capacity
        self.device = device if device else torch.device('cpu')
        
        # Pre-allocate numpy arrays for fast inserts
        self.states = np.zeros((capacity, state_dim), dtype=np.float32)
        self.actions = np.zeros((capacity, action_dim), dtype=np.float32)
        self.rewards = np.zeros((capacity, 1), dtype=np.float32)
        self.next_states = np.zeros((capacity, state_dim), dtype=np.float32)
        self.dones = np.zeros((capacity, 1), dtype=np.float32)
        
        self.ptr = 0
        self.size = 0

    def add(self, state: np.ndarray, action: np.ndarray, reward: float, next_state: np.ndarray, done: bool):
        """
        Inserts a single transition into the cyclic buffer.
        """
        self.states[self.ptr] = state
        self.actions[self.ptr] = action
        self.rewards[self.ptr] = reward
        self.next_states[self.ptr] = next_state
        self.dones[self.ptr] = float(done)
        
        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size: int):
        """
        Samples a random mini-batch of transitions.
        Returns PyTorch tensors mapped to the target compute device.
        """
        # Randomly select indices
        indices = np.random.randint(0, self.size, size=batch_size)
        
        # Extract batch
        batch_states = torch.FloatTensor(self.states[indices]).to(self.device)
        batch_actions = torch.FloatTensor(self.actions[indices]).to(self.device)
        batch_rewards = torch.FloatTensor(self.rewards[indices]).to(self.device)
        batch_next_states = torch.FloatTensor(self.next_states[indices]).to(self.device)
        batch_dones = torch.FloatTensor(self.dones[indices]).to(self.device)
        
        return batch_states, batch_actions, batch_rewards, batch_next_states, batch_dones

    def __len__(self):
        return self.size
