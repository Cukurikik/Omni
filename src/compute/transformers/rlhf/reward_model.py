"""
OMNI Transformer — Reward Model for RLHF
Bradley-Terry preference model for reinforcement learning from human feedback.
Learned from: Shekswess/tiny-reasoning-language-model (TRL/DPO)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class RewardModelConfig:
    base_model_dim: int = 768
    num_layers: int = 6
    num_heads: int = 12
    dropout: float = 0.1


class RewardHead(nn.Module):
    """Scalar reward prediction head."""
    def __init__(self, input_dim: int, dropout: float = 0.1):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, input_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(input_dim // 2, 1),
        )

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        # Pool: use last non-padding token
        return self.layers(hidden_states).squeeze(-1)


class OmniRewardModel(nn.Module):
    """Reward model for RLHF preference learning."""
    def __init__(self, base_model: nn.Module, config: RewardModelConfig):
        super().__init__()
        self.base_model = base_model
        self.reward_head = RewardHead(config.base_model_dim, config.dropout)
        # Freeze base model
        for param in self.base_model.parameters():
            param.requires_grad = False

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
        hidden = outputs.get("last_hidden_state", outputs.get("logits", None))
        if hidden is None:
            raise ValueError("Base model must return hidden states")
        # Pool to last token
        if attention_mask is not None:
            last_idx = attention_mask.sum(dim=1) - 1
            pooled = hidden[torch.arange(hidden.size(0), device=hidden.device), last_idx]
        else:
            pooled = hidden[:, -1]
        return self.reward_head(pooled)

    @staticmethod
    def compute_preference_loss(chosen_rewards: torch.Tensor, rejected_rewards: torch.Tensor) -> torch.Tensor:
        """Bradley-Terry preference loss: log sigmoid(r_chosen - r_rejected)."""
        return -F.logsigmoid(chosen_rewards - rejected_rewards).mean()


class DPOTrainer:
    """Direct Preference Optimization (DPO) trainer."""
    def __init__(self, model: nn.Module, ref_model: nn.Module, beta: float = 0.1):
        self.model = model
        self.ref_model = ref_model
        self.ref_model.eval()
        self.beta = beta

    def compute_dpo_loss(self, chosen_ids: torch.Tensor, rejected_ids: torch.Tensor,
                         chosen_mask: Optional[torch.Tensor] = None,
                         rejected_mask: Optional[torch.Tensor] = None) -> Dict:
        # Policy log probs
        chosen_logps = self._get_log_probs(self.model, chosen_ids, chosen_mask)
        rejected_logps = self._get_log_probs(self.model, rejected_ids, rejected_mask)

        # Reference log probs
        with torch.inference_mode():
            ref_chosen_logps = self._get_log_probs(self.ref_model, chosen_ids, chosen_mask)
            ref_rejected_logps = self._get_log_probs(self.ref_model, rejected_ids, rejected_mask)

        # DPO loss
        chosen_rewards = self.beta * (chosen_logps - ref_chosen_logps)
        rejected_rewards = self.beta * (rejected_logps - ref_rejected_logps)
        loss = -F.logsigmoid(chosen_rewards - rejected_rewards).mean()

        return {"loss": loss, "chosen_rewards": chosen_rewards.mean().item(),
                "rejected_rewards": rejected_rewards.mean().item()}

    @staticmethod
    def _get_log_probs(model: nn.Module, input_ids: torch.Tensor,
                       attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs["logits"] if isinstance(outputs, dict) else outputs
        log_probs = F.log_softmax(logits[:, :-1], dim=-1)
        target_log_probs = torch.gather(log_probs, 2, input_ids[:, 1:].unsqueeze(-1)).squeeze(-1)
        if attention_mask is not None:
            target_log_probs = target_log_probs * attention_mask[:, 1:]
        return target_log_probs.sum(dim=-1)
