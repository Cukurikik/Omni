"""
OMNI MOTHER: RLHF Reward Model (Production Grade)
Scores text sequences for alignment quality. Trained on human preference
pairs to provide scalar reward signals for PPO.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple
import logging

logger = logging.getLogger("OmniReward")

class RewardHead(nn.Module):
    """Scalar reward head attached to a frozen LM backbone."""
    def __init__(self, hidden_size: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(hidden_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.out = nn.Linear(hidden_size // 2, 1)
        self.dropout = nn.Dropout(dropout)
        self.act = nn.GELU()

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        x = self.dropout(self.act(self.fc1(hidden)))
        x = self.dropout(self.act(self.fc2(x)))
        return self.out(x).squeeze(-1)

class OmniRewardModel(nn.Module):
    """End-to-end reward model: backbone + reward head."""
    def __init__(self, backbone: nn.Module, hidden_size: int,
                 pad_token_id: int = 0, freeze_backbone: bool = True):
        super().__init__()
        self.backbone = backbone
        self.reward_head = RewardHead(hidden_size)
        self.pad_token_id = pad_token_id
        if freeze_backbone:
            for p in self.backbone.parameters():
                p.requires_grad = False

    def _get_last_hidden(self, input_ids: torch.Tensor) -> torch.Tensor:
        outputs = self.backbone(input_ids)
        if isinstance(outputs, tuple):
            hidden = outputs[0]
        elif hasattr(outputs, 'last_hidden_state'):
            hidden = outputs.last_hidden_state
        else:
            hidden = outputs
        # Use last non-pad token
        mask = (input_ids != self.pad_token_id).long()
        lengths = mask.sum(dim=-1) - 1
        batch_idx = torch.arange(hidden.size(0), device=hidden.device)
        return hidden[batch_idx, lengths]

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        last_hidden = self._get_last_hidden(input_ids)
        return self.reward_head(last_hidden)

    def preference_loss(self, chosen_ids: torch.Tensor,
                        rejected_ids: torch.Tensor,
                        margin: float = 0.0) -> Tuple[torch.Tensor, Dict]:
        """Bradley-Terry pairwise ranking loss."""
        r_chosen = self.forward(chosen_ids)
        r_rejected = self.forward(rejected_ids)
        loss = -F.logsigmoid(r_chosen - r_rejected - margin).mean()
        with torch.no_grad():
            acc = (r_chosen > r_rejected).float().mean()
        return loss, {
            "loss": loss.item(),
            "accuracy": acc.item(),
            "reward_chosen": r_chosen.mean().item(),
            "reward_rejected": r_rejected.mean().item(),
            "reward_margin": (r_chosen - r_rejected).mean().item(),
        }
