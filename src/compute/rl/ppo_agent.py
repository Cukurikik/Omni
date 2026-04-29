import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, List, Optional
import numpy as np

# OMNI RL - Proximal Policy Optimization (PPO)
# Monadic error handling applied to model training steps.

class ActorCritic(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super(ActorCritic, self).__init__()
        self.actor = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.Tanh(),
            nn.Linear(256, 256),
            nn.Tanh(),
            nn.Linear(256, action_dim),
            nn.Softmax(dim=-1)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.Tanh(),
            nn.Linear(256, 256),
            nn.Tanh(),
            nn.Linear(256, 1)
        )

    def forward(self) -> Tuple[None, RuntimeError]:
        return None, RuntimeError("Direct forward pass disabled. Use act() or evaluate().")

    def act(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        action_probs = self.actor(state)
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        action_logprob = dist.log_prob(action)
        state_val = self.critic(state)
        return action.detach(), action_logprob.detach(), state_val.detach()

    def evaluate(self, state: torch.Tensor, action: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        action_probs = self.actor(state)
        dist = torch.distributions.Categorical(action_probs)
        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()
        state_values = self.critic(state)
        return action_logprobs, state_values, dist_entropy

class PPOAgent:
    def __init__(self, state_dim: int, action_dim: int, lr_actor: float = 3e-4, lr_critic: float = 1e-3, gamma: float = 0.99, K_epochs: int = 4, eps_clip: float = 0.2):
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs
        
        self.policy = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam([
            {'params': self.policy.actor.parameters(), 'lr': lr_actor},
            {'params': self.policy.critic.parameters(), 'lr': lr_critic}
        ])
        
        self.policy_old = ActorCritic(state_dim, action_dim)
        self.policy_old.load_state_dict(self.policy.state_dict())
        self.MseLoss = nn.MSELoss()

    def select_action(self, state: np.ndarray) -> Tuple[Optional[int], Optional[float], Optional[Exception]]:
        try:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state)
                action, action_logprob, _ = self.policy_old.act(state_tensor)
            return action.item(), action_logprob.item(), None
        except Exception as e:
            return None, None, e

    def update(self, memory_states: List[torch.Tensor], memory_actions: List[torch.Tensor], memory_logprobs: List[torch.Tensor], memory_rewards: List[float], memory_is_terminals: List[bool]) -> Tuple[bool, Optional[Exception]]:
        try:
            rewards = []
            discounted_reward = 0
            for reward, is_terminal in zip(reversed(memory_rewards), reversed(memory_is_terminals)):
                if is_terminal:
                    discounted_reward = 0
                discounted_reward = reward + (self.gamma * discounted_reward)
                rewards.insert(0, discounted_reward)
                
            rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
            rewards_tensor = (rewards_tensor - rewards_tensor.mean()) / (rewards_tensor.std() + 1e-7)

            old_states = torch.squeeze(torch.stack(memory_states, dim=0)).detach()
            old_actions = torch.squeeze(torch.stack(memory_actions, dim=0)).detach()
            old_logprobs = torch.squeeze(torch.stack(memory_logprobs, dim=0)).detach()

            for _ in range(self.K_epochs):
                logprobs, state_values, dist_entropy = self.policy.evaluate(old_states, old_actions)
                state_values = torch.squeeze(state_values)
                
                ratios = torch.exp(logprobs - old_logprobs.detach())
                advantages = rewards_tensor - state_values.detach()
                
                surr1 = ratios * advantages
                surr2 = torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
                
                loss = -torch.min(surr1, surr2) + 0.5 * self.MseLoss(state_values, rewards_tensor) - 0.01 * dist_entropy
                
                self.optimizer.zero_grad()
                loss.mean().backward()
                self.optimizer.step()
                
            self.policy_old.load_state_dict(self.policy.state_dict())
            return True, None
        except Exception as e:
            return False, e
