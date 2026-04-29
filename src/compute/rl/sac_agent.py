import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Normal
from typing import Tuple, Optional
import numpy as np

# OMNI RL - Soft Actor-Critic (SAC) Agent
# Monadic error handling applied to model training steps.

LOG_SIG_MAX = 2
LOG_SIG_MIN = -20
epsilon = 1e-6

class SACActor(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super(SACActor, self).__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.mean_linear = nn.Linear(hidden_dim, action_dim)
        self.log_std_linear = nn.Linear(hidden_dim, action_dim)

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        mean = self.mean_linear(x)
        log_std = self.log_std_linear(x)
        log_std = torch.clamp(log_std, min=LOG_SIG_MIN, max=LOG_SIG_MAX)
        return mean, log_std

    def sample(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mean, log_std = self.forward(state)
        std = log_std.exp()
        normal = Normal(mean, std)
        x_t = normal.rsample()  # for reparameterization trick
        y_t = torch.tanh(x_t)
        action = y_t
        log_prob = normal.log_prob(x_t)
        # Enforcing Action Bound
        log_prob -= torch.log(1 - action.pow(2) + epsilon)
        log_prob = log_prob.sum(1, keepdim=True)
        mean = torch.tanh(mean)
        return action, log_prob, mean

class SACCritic(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super(SACCritic, self).__init__()
        # Q1 architecture
        self.fc1 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)

        # Q2 architecture
        self.fc4 = nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc5 = nn.Linear(hidden_dim, hidden_dim)
        self.fc6 = nn.Linear(hidden_dim, 1)

    def forward(self, state: torch.Tensor, action: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        xu = torch.cat([state, action], 1)
        
        x1 = F.relu(self.fc1(xu))
        x1 = F.relu(self.fc2(x1))
        q1 = self.fc3(x1)

        x2 = F.relu(self.fc4(xu))
        x2 = F.relu(self.fc5(x2))
        q2 = self.fc6(x2)

        return q1, q2

class SACAgent:
    def __init__(self, state_dim: int, action_dim: int, gamma: float = 0.99, tau: float = 0.005, alpha: float = 0.2):
        self.gamma = gamma
        self.tau = tau
        self.alpha = alpha

        self.actor = SACActor(state_dim, action_dim)
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=3e-4)

        self.critic = SACCritic(state_dim, action_dim)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=3e-4)

        self.critic_target = SACCritic(state_dim, action_dim)
        self.critic_target.load_state_dict(self.critic.state_dict())

    def update_parameters(self, state_batch: torch.Tensor, action_batch: torch.Tensor, reward_batch: torch.Tensor, next_state_batch: torch.Tensor, mask_batch: torch.Tensor) -> Tuple[bool, Optional[Exception]]:
        try:
            with torch.no_grad():
                next_state_action, next_state_log_pi, _ = self.actor.sample(next_state_batch)
                qf1_next_target, qf2_next_target = self.critic_target(next_state_batch, next_state_action)
                min_qf_next_target = torch.min(qf1_next_target, qf2_next_target) - self.alpha * next_state_log_pi
                next_q_value = reward_batch + mask_batch * self.gamma * (min_qf_next_target)

            qf1, qf2 = self.critic(state_batch, action_batch)
            qf1_loss = F.mse_loss(qf1, next_q_value)
            qf2_loss = F.mse_loss(qf2, next_q_value)
            qf_loss = qf1_loss + qf2_loss

            self.critic_optimizer.zero_grad()
            qf_loss.backward()
            self.critic_optimizer.step()

            pi, log_pi, _ = self.actor.sample(state_batch)
            qf1_pi, qf2_pi = self.critic(state_batch, pi)
            min_qf_pi = torch.min(qf1_pi, qf2_pi)
            policy_loss = ((self.alpha * log_pi) - min_qf_pi).mean()

            self.actor_optimizer.zero_grad()
            policy_loss.backward()
            self.actor_optimizer.step()

            for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
                target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

            return True, None
        except Exception as e:
            return False, e
