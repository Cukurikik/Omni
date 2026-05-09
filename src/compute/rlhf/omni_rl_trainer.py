"""
omni_rl_trainer.py — Reinforcement Learning from Human Feedback
Inspired by: PPO/DPO training for OMNI model alignment
Layer: Compute / AI

RLHF training loop with PPO policy optimization, reward model
scoring, KL divergence penalty, and advantage normalization.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import math


@dataclass
class RLHFConfig:
    clip_range: float = 0.2
    clip_range_vf: float = 0.2
    gamma: float = 1.0
    gae_lambda: float = 0.95
    kl_penalty_coef: float = 0.1
    kl_target: float = 6.0
    entropy_coef: float = 0.01
    value_coef: float = 0.5
    max_grad_norm: float = 1.0
    ppo_epochs: int = 4
    mini_batch_size: int = 8
    adaptive_kl: bool = True


class RewardScaler:
    """Running normalization of reward signals."""

    def __init__(self, clip: float = 10.0, gamma: float = 0.99):
        self.running_mean = 0.0
        self.running_var = 1.0
        self.count = 0
        self.clip = clip
        self.gamma = gamma

    def normalize(self, rewards: torch.Tensor) -> torch.Tensor:
        batch_mean = rewards.mean().item()
        batch_var = rewards.var().item() + 1e-8

        # Update running statistics
        self.count += 1
        delta = batch_mean - self.running_mean
        self.running_mean += delta / self.count
        self.running_var = self.gamma * self.running_var + (1 - self.gamma) * batch_var

        std = math.sqrt(self.running_var + 1e-8)
        normalized = (rewards - self.running_mean) / std
        return torch.clamp(normalized, -self.clip, self.clip)


class GAECalculator:
    """Generalized Advantage Estimation."""

    def __init__(self, gamma: float = 1.0, gae_lambda: float = 0.95):
        self.gamma = gamma
        self.gae_lambda = gae_lambda

    def compute(self, rewards: torch.Tensor, values: torch.Tensor,
                dones: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute advantages and returns.

        Args:
            rewards: (batch, seq_len) reward signals
            values: (batch, seq_len) value estimates
            dones: (batch, seq_len) episode termination flags

        Returns:
            advantages: (batch, seq_len)
            returns: (batch, seq_len)
        """
        B, T = rewards.shape
        if dones is None:
            dones = torch.zeros_like(rewards)

        advantages = torch.zeros_like(rewards)
        last_gae = torch.zeros(B, device=rewards.device)

        for t in reversed(range(T)):
            if t == T - 1:
                next_value = torch.zeros(B, device=rewards.device)
            else:
                next_value = values[:, t + 1]

            delta = rewards[:, t] + self.gamma * next_value * (1 - dones[:, t]) - values[:, t]
            last_gae = delta + self.gamma * self.gae_lambda * (1 - dones[:, t]) * last_gae
            advantages[:, t] = last_gae

        returns = advantages + values
        return advantages, returns


class AdaptiveKLController:
    """Dynamically adjust KL penalty coefficient."""

    def __init__(self, init_coef: float = 0.1, target: float = 6.0,
                 horizon: int = 10000):
        self.coef = init_coef
        self.target = target
        self.horizon = horizon

    def update(self, current_kl: float):
        proportional_error = (current_kl - self.target) / self.target
        mult = 1.0 + proportional_error / self.horizon
        self.coef *= mult
        self.coef = max(0.001, min(self.coef, 10.0))


class OmniRLHFTrainer:
    """PPO-based RLHF trainer for language model alignment.

    Implements:
    - Clipped PPO objective
    - GAE advantage estimation
    - Adaptive KL penalty
    - Reward normalization
    - Mini-batch training with multiple epochs
    """

    def __init__(self, policy_model: nn.Module, value_model: nn.Module,
                 ref_model: nn.Module, config: RLHFConfig = RLHFConfig()):
        self.policy = policy_model
        self.value = value_model
        self.ref = ref_model
        self.config = config

        self.gae = GAECalculator(config.gamma, config.gae_lambda)
        self.reward_scaler = RewardScaler()
        self.kl_controller = AdaptiveKLController(
            config.kl_penalty_coef, config.kl_target
        ) if config.adaptive_kl else None

        # Freeze reference model
        for param in self.ref.parameters():
            param.requires_grad = False

    @torch.no_grad()
    def compute_kl_divergence(self, policy_logprobs: torch.Tensor,
                              ref_logprobs: torch.Tensor) -> torch.Tensor:
        """Compute per-token KL divergence between policy and reference."""
        return policy_logprobs - ref_logprobs

    @torch.no_grad()
    def compute_rewards(self, reward_scores: torch.Tensor,
                        kl_divergence: torch.Tensor) -> torch.Tensor:
        """Compute final rewards with KL penalty."""
        kl_coef = (self.kl_controller.coef if self.kl_controller
                   else self.config.kl_penalty_coef)
        rewards = reward_scores - kl_coef * kl_divergence
        return self.reward_scaler.normalize(rewards)

    def ppo_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Execute one PPO training step.

        Args:
            batch: dict with keys:
                - input_ids: (B, T) token IDs
                - attention_mask: (B, T)
                - old_logprobs: (B, T) log-probabilities from rollout
                - old_values: (B, T) value estimates from rollout
                - rewards: (B, T) reward signals
                - advantages: (B, T) pre-computed advantages
                - returns: (B, T) pre-computed returns

        Returns:
            dict with training metrics
        """
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        old_logprobs = batch["old_logprobs"]
        old_values = batch["old_values"]
        advantages = batch["advantages"]
        returns = batch["returns"]

        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        total_kl = 0.0
        num_updates = 0

        B = input_ids.shape[0]

        for epoch in range(self.config.ppo_epochs):
            indices = torch.randperm(B, device=input_ids.device)

            for start in range(0, B, self.config.mini_batch_size):
                end = min(start + self.config.mini_batch_size, B)
                mb_indices = indices[start:end]

                mb_input = input_ids[mb_indices]
                mb_mask = attention_mask[mb_indices]
                mb_old_logprobs = old_logprobs[mb_indices]
                mb_old_values = old_values[mb_indices]
                mb_advantages = advantages[mb_indices]
                mb_returns = returns[mb_indices]

                # Forward pass through policy
                policy_output = self.policy(mb_input, attention_mask=mb_mask)
                logits = policy_output.logits if hasattr(policy_output, 'logits') else policy_output

                # Compute new log-probabilities
                new_logprobs = F.log_softmax(logits, dim=-1)
                token_logprobs = new_logprobs.gather(
                    -1, mb_input.unsqueeze(-1)
                ).squeeze(-1)

                # Compute entropy
                entropy = -(new_logprobs * new_logprobs.exp()).sum(dim=-1).mean()

                # PPO clipped objective
                ratio = (token_logprobs - mb_old_logprobs).exp()
                surr1 = ratio * mb_advantages
                surr2 = torch.clamp(ratio, 1 - self.config.clip_range,
                                    1 + self.config.clip_range) * mb_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                new_values = self.value(mb_input, attention_mask=mb_mask)
                if hasattr(new_values, 'logits'):
                    new_values = new_values.logits.squeeze(-1)
                elif isinstance(new_values, torch.Tensor) and new_values.dim() > 2:
                    new_values = new_values.squeeze(-1)

                # Clipped value loss
                if new_values.shape != mb_returns.shape:
                    new_values = new_values[:, :mb_returns.shape[1]]

                value_clipped = mb_old_values + torch.clamp(
                    new_values - mb_old_values,
                    -self.config.clip_range_vf,
                    self.config.clip_range_vf,
                )
                vf_loss1 = (new_values - mb_returns).pow(2)
                vf_loss2 = (value_clipped - mb_returns).pow(2)
                value_loss = torch.max(vf_loss1, vf_loss2).mean()

                # KL divergence
                kl = (mb_old_logprobs - token_logprobs).mean()

                # Total loss
                loss = (policy_loss
                        + self.config.value_coef * value_loss
                        - self.config.entropy_coef * entropy)

                total_policy_loss += policy_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += entropy.item()
                total_kl += kl.item()
                num_updates += 1

                # NOTE: Backward pass and optimizer step handled by caller
                # loss.backward() + optimizer.step()

        # Update adaptive KL controller
        avg_kl = total_kl / max(num_updates, 1)
        if self.kl_controller:
            self.kl_controller.update(avg_kl)

        return {
            "policy_loss": total_policy_loss / max(num_updates, 1),
            "value_loss": total_value_loss / max(num_updates, 1),
            "entropy": total_entropy / max(num_updates, 1),
            "kl_divergence": avg_kl,
            "kl_coef": self.kl_controller.coef if self.kl_controller else self.config.kl_penalty_coef,
        }

    @torch.no_grad()
    def generate_rollout(self, prompts: torch.Tensor,
                         max_new_tokens: int = 128) -> Dict[str, torch.Tensor]:
        """Generate responses from policy and compute rollout statistics."""
        self.policy.eval()
        self.value.eval()

        # Simple greedy/sampling generation (production would use beam search)
        generated = prompts.clone()
        all_logprobs = []

        for _ in range(max_new_tokens):
            output = self.policy(generated)
            logits = output.logits if hasattr(output, 'logits') else output
            next_token_logits = logits[:, -1, :]

            probs = F.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, 1)
            log_prob = F.log_softmax(next_token_logits, dim=-1)
            token_log_prob = log_prob.gather(-1, next_token).squeeze(-1)

            all_logprobs.append(token_log_prob)
            generated = torch.cat([generated, next_token], dim=-1)

        self.policy.train()
        self.value.train()

        return {
            "sequences": generated,
            "logprobs": torch.stack(all_logprobs, dim=1),
        }
