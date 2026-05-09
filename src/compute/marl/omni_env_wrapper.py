"""
omni_env_wrapper.py — MAPPO Environment Wrapper
Layer: Compute / AI

Wraps physical simulation environments (like MuJoCo or the OMNI physics engine)
into a vectorized, multi-agent format compatible with the MAPPO training loop.
"""

import numpy as np
from typing import List, Tuple, Dict

class OmniMultiAgentEnvWrapper:
    """
    Standardizes the interface for multi-agent environments.
    Expects step() to return observations, rewards, dones, and infos for ALL agents.
    """
    def __init__(self, num_agents: int, obs_dim: int, action_dim: int):
        self.num_agents = num_agents
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        
        # Mock internal state for the environment simulator
        self.current_step = 0
        self.max_steps = 1000

    def reset(self) -> np.ndarray:
        """
        Resets the environment.
        Returns: Global observation matrix of shape (num_agents, obs_dim)
        """
        self.current_step = 0
        return np.zeros((self.num_agents, self.obs_dim), dtype=np.float32)

    def step(self, actions: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict]:
        """
        Takes a step in the environment.
        actions: (num_agents, action_dim)
        
        Returns:
            obs: (num_agents, obs_dim)
            rewards: (num_agents,)
            dones: (num_agents,)
            info: dict
        """
        assert actions.shape == (self.num_agents, self.action_dim)
        
        self.current_step += 1
        
        # Mock physics transition
        next_obs = np.random.randn(self.num_agents, self.obs_dim).astype(np.float32)
        
        # Mock reward calculation (e.g., forward velocity penalty)
        rewards = np.sum(actions ** 2, axis=1) * -0.1 
        
        # Check termination
        done_flag = self.current_step >= self.max_steps
        dones = np.full((self.num_agents,), done_flag, dtype=bool)
        
        return next_obs, rewards, dones, {"step": self.current_step}

    def get_global_state(self) -> np.ndarray:
        """
        Returns the concatenated global state for the Centralized Critic in MAPPO.
        Shape: (num_agents * obs_dim,)
        """
        # In a real environment, this might contain privileged information 
        # (e.g., exact object positions) not visible in local obs.
        obs = np.random.randn(self.num_agents * self.obs_dim).astype(np.float32)
        return obs
