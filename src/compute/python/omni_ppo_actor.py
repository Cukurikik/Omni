"""
OMNI MOTHER: PPO Actor for RLHF (Production Grade)
Proximal Policy Optimization for language model alignment.
Implements clipped surrogate objective, GAE, value head, and KL penalty.
Ref: Schulman et al. (2017), InstructGPT (Ouyang et al., 2022)
"""
import logging
from typing import Dict, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("OmniPPO")

class ValueHead(nn.Module):
    """Scalar value head attached to the LM backbone for advantage estimation."""
    def __init__(self, hidden_size: int, dropout: float = 0.1):
        super().__init__()
        self.dense = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.value_out = nn.Linear(hidden_size, 1)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        x = self.dropout(torch.tanh(self.dense(hidden_states)))
        return self.value_out(x).squeeze(-1)

class PPOActor:
    """Orchestrates PPO training for RLHF."""
    def __init__(self, policy: nn.Module, value_head: ValueHead,
                 ref_model: nn.Module, clip_eps: float = 0.2,
                 vf_coeff: float = 0.5, kl_coeff: float = 0.1,
                 gamma: float = 1.0, lam: float = 0.95,
                 target_kl: Optional[float] = None):
        self.policy = policy
        self.value_head = value_head
        self.ref = ref_model
        self.clip_eps = clip_eps
        self.vf_coeff = vf_coeff
        self.kl_coeff = kl_coeff
        self.gamma = gamma
        self.lam = lam
        self.target_kl = target_kl
        for p in self.ref.parameters():
            p.requires_grad = False

    @staticmethod
    def _gather_logprobs(logits: torch.Tensor, ids: torch.Tensor) -> torch.Tensor:
        return F.log_softmax(logits, dim=-1).gather(-1, ids.unsqueeze(-1)).squeeze(-1)

    def compute_advantages(self, rewards: torch.Tensor, values: torch.Tensor,
                           mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Generalized Advantage Estimation (GAE-λ)."""
        T = rewards.size(-1)
        advantages = torch.zeros_like(rewards)
        last_gae = 0.0
        for t in reversed(range(T)):
            next_val = values[:, t + 1] if t + 1 < values.size(-1) else 0.0
            delta = rewards[:, t] + self.gamma * next_val - values[:, t]
            last_gae = delta + self.gamma * self.lam * last_gae
            advantages[:, t] = last_gae * mask[:, t]
        returns = advantages + values[:, :T]
        return advantages, returns

    def compute_loss(self, input_ids: torch.Tensor, response_ids: torch.Tensor,
                     old_logprobs: torch.Tensor, rewards: torch.Tensor,
                     mask: torch.Tensor) -> Tuple[torch.Tensor, Dict]:
        # Forward
        full_ids = torch.cat([input_ids, response_ids], dim=-1)
        logits = self.policy(full_ids)
        if logits.dim() == 3:
            resp_logits = logits[:, input_ids.size(-1)-1:-1, :]
        else:
            resp_logits = logits
        new_logprobs = self._gather_logprobs(resp_logits, response_ids)

        # Value
        hidden = logits if logits.dim() == 2 else logits[:, input_ids.size(-1)-1:-1, :]
        values = self.value_head(hidden.detach())
        advantages, returns = self.compute_advantages(rewards, values, mask)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # PPO clipped surrogate
        ratio = torch.exp(new_logprobs - old_logprobs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()

        # Value loss
        value_loss = F.mse_loss(values[:, :returns.size(-1)], returns)

        # KL penalty
        with torch.no_grad():
            ref_logits = self.ref(full_ids)
            if ref_logits.dim() == 3:
                ref_resp = ref_logits[:, input_ids.size(-1)-1:-1, :]
            else:
                ref_resp = ref_logits
            ref_logprobs = self._gather_logprobs(ref_resp, response_ids)
        kl = (new_logprobs - ref_logprobs).mean()

        total = policy_loss + self.vf_coeff * value_loss + self.kl_coeff * kl

        metrics = {
            "policy_loss": policy_loss.item(),
            "value_loss": value_loss.item(),
            "kl_divergence": kl.item(),
            "mean_advantage": advantages.mean().item(),
            "clip_fraction": ((ratio - 1).abs() > self.clip_eps).float().mean().item(),
        }

        # Adaptive KL penalty
        if self.target_kl is not None:
            if kl.item() > 1.5 * self.target_kl:
                self.kl_coeff *= 2.0
            elif kl.item() < self.target_kl / 1.5:
                self.kl_coeff *= 0.5
            metrics["kl_coeff"] = self.kl_coeff

        return total, metrics
