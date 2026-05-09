"""
omni_dpo_trainer.py — Direct Preference Optimization
Inspired by: DPO paper + OMNI alignment training
Layer: Compute / AI

Direct Preference Optimization for LLM alignment without
explicit reward modeling — learns directly from preference pairs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DPOConfig:
    beta: float = 0.1           # Temperature parameter
    label_smoothing: float = 0.0
    loss_type: str = "sigmoid"  # "sigmoid", "hinge", "ipo"
    reference_free: bool = False
    max_length: int = 2048
    max_prompt_length: int = 512


class OmniDPOTrainer:
    """Direct Preference Optimization trainer.

    Directly optimizes the policy from preference pairs (chosen, rejected)
    without fitting a separate reward model, using the log-ratio
    of policy/reference probabilities.
    """

    def __init__(self, policy_model: nn.Module, ref_model: nn.Module,
                 config: DPOConfig = DPOConfig()):
        self.policy = policy_model
        self.ref = ref_model
        self.config = config

        # Freeze reference model
        for param in self.ref.parameters():
            param.requires_grad = False

    def compute_logprobs(self, model: nn.Module, input_ids: torch.Tensor,
                         attention_mask: torch.Tensor,
                         labels: torch.Tensor) -> torch.Tensor:
        """Compute per-token log-probabilities for given labels."""
        output = model(input_ids, attention_mask=attention_mask)
        logits = output.logits if hasattr(output, 'logits') else output

        # Shift for autoregressive: predict next token
        shift_logits = logits[:, :-1, :]
        shift_labels = labels[:, 1:]

        log_probs = F.log_softmax(shift_logits, dim=-1)
        per_token_logps = log_probs.gather(-1, shift_labels.unsqueeze(-1)).squeeze(-1)

        # Mask out padding
        loss_mask = (shift_labels != -100).float()
        per_sequence_logps = (per_token_logps * loss_mask).sum(dim=-1)

        return per_sequence_logps

    def dpo_loss(self, policy_chosen_logps: torch.Tensor,
                 policy_rejected_logps: torch.Tensor,
                 ref_chosen_logps: torch.Tensor,
                 ref_rejected_logps: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Compute DPO loss from log-probability pairs.

        Args:
            policy_chosen_logps: log P_policy(chosen)
            policy_rejected_logps: log P_policy(rejected)
            ref_chosen_logps: log P_ref(chosen)
            ref_rejected_logps: log P_ref(rejected)

        Returns:
            loss: scalar DPO loss
            metrics: dict with training metrics
        """
        # Log-ratio differences
        pi_logratios = policy_chosen_logps - policy_rejected_logps
        ref_logratios = ref_chosen_logps - ref_rejected_logps

        if self.config.reference_free:
            ref_logratios = 0.0

        logits = pi_logratios - ref_logratios

        if self.config.loss_type == "sigmoid":
            loss = -F.logsigmoid(self.config.beta * logits)
        elif self.config.loss_type == "hinge":
            loss = torch.relu(1 - self.config.beta * logits)
        elif self.config.loss_type == "ipo":
            # Identity Preference Optimization
            loss = (logits - 1 / (2 * self.config.beta)).pow(2)
        else:
            raise ValueError(f"Unknown loss type: {self.config.loss_type}")

        # Label smoothing
        if self.config.label_smoothing > 0:
            smooth_loss = -F.logsigmoid(-self.config.beta * logits)
            loss = (1 - self.config.label_smoothing) * loss + self.config.label_smoothing * smooth_loss

        loss = loss.mean()

        # Metrics
        with torch.no_grad():
            chosen_rewards = (policy_chosen_logps - ref_chosen_logps).detach()
            rejected_rewards = (policy_rejected_logps - ref_rejected_logps).detach()
            reward_accuracies = (chosen_rewards > rejected_rewards).float().mean()
            reward_margin = (chosen_rewards - rejected_rewards).mean()

        metrics = {
            "loss": loss.item(),
            "reward_accuracy": reward_accuracies.item(),
            "reward_margin": reward_margin.item(),
            "chosen_reward": chosen_rewards.mean().item(),
            "rejected_reward": rejected_rewards.mean().item(),
            "logits_mean": logits.mean().item(),
            "logits_std": logits.std().item(),
        }

        return loss, metrics

    def training_step(self, batch: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Execute one DPO training step.

        Expected batch keys:
            - chosen_input_ids, chosen_attention_mask, chosen_labels
            - rejected_input_ids, rejected_attention_mask, rejected_labels
        """
        # Compute policy log-probs
        policy_chosen_logps = self.compute_logprobs(
            self.policy,
            batch["chosen_input_ids"],
            batch["chosen_attention_mask"],
            batch["chosen_labels"],
        )

        policy_rejected_logps = self.compute_logprobs(
            self.policy,
            batch["rejected_input_ids"],
            batch["rejected_attention_mask"],
            batch["rejected_labels"],
        )

        # Compute reference log-probs (no grad)
        with torch.no_grad():
            ref_chosen_logps = self.compute_logprobs(
                self.ref,
                batch["chosen_input_ids"],
                batch["chosen_attention_mask"],
                batch["chosen_labels"],
            )

            ref_rejected_logps = self.compute_logprobs(
                self.ref,
                batch["rejected_input_ids"],
                batch["rejected_attention_mask"],
                batch["rejected_labels"],
            )

        loss, metrics = self.dpo_loss(
            policy_chosen_logps, policy_rejected_logps,
            ref_chosen_logps, ref_rejected_logps,
        )

        return loss, metrics

    @torch.no_grad()
    def evaluate(self, eval_batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Evaluate DPO metrics on a batch."""
        self.policy.eval()

        policy_chosen_logps = self.compute_logprobs(
            self.policy,
            eval_batch["chosen_input_ids"],
            eval_batch["chosen_attention_mask"],
            eval_batch["chosen_labels"],
        )
        policy_rejected_logps = self.compute_logprobs(
            self.policy,
            eval_batch["rejected_input_ids"],
            eval_batch["rejected_attention_mask"],
            eval_batch["rejected_labels"],
        )
        ref_chosen_logps = self.compute_logprobs(
            self.ref,
            eval_batch["chosen_input_ids"],
            eval_batch["chosen_attention_mask"],
            eval_batch["chosen_labels"],
        )
        ref_rejected_logps = self.compute_logprobs(
            self.ref,
            eval_batch["rejected_input_ids"],
            eval_batch["rejected_attention_mask"],
            eval_batch["rejected_labels"],
        )

        _, metrics = self.dpo_loss(
            policy_chosen_logps, policy_rejected_logps,
            ref_chosen_logps, ref_rejected_logps,
        )

        self.policy.train()
        return metrics
