"""
OMNI MOTHER: DPO Trainer (Production Grade)
Ref: Rafailov et al., 2023 — Direct Preference Optimization
"""
import torch, torch.nn as nn, torch.nn.functional as F
from typing import Dict, Tuple
import logging
logger = logging.getLogger("OmniDPO")

class OmniDPOTrainer:
    def __init__(self, policy: nn.Module, ref: nn.Module, beta: float = 0.1,
                 label_smoothing: float = 0.0, loss_type: str = "sigmoid"):
        self.policy, self.ref, self.beta = policy, ref, beta
        self.label_smoothing, self.loss_type = label_smoothing, loss_type
        for p in self.ref.parameters(): p.requires_grad = False

    @staticmethod
    def _logps(logits: torch.Tensor, ids: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        lp = F.log_softmax(logits, dim=-1).gather(-1, ids.unsqueeze(-1)).squeeze(-1)
        return (lp * mask).sum(dim=-1)

    def compute_loss(self, batch: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict]:
        cids, cmask = batch["chosen_ids"], batch["chosen_mask"]
        rids, rmask = batch["rejected_ids"], batch["rejected_mask"]
        pi_c = self._logps(self.policy(cids)[:, :-1], cids[:, 1:], cmask[:, 1:])
        pi_r = self._logps(self.policy(rids)[:, :-1], rids[:, 1:], rmask[:, 1:])
        with torch.no_grad():
            ref_c = self._logps(self.ref(cids)[:, :-1], cids[:, 1:], cmask[:, 1:])
            ref_r = self._logps(self.ref(rids)[:, :-1], rids[:, 1:], rmask[:, 1:])
        logits = (pi_c - pi_r) - (ref_c - ref_r)
        if self.loss_type == "hinge":
            loss = torch.relu(1.0 - self.beta * logits).mean()
        elif self.loss_type == "ipo":
            loss = ((logits - 1/(2*self.beta))**2).mean()
        else:
            loss = -F.logsigmoid(self.beta * logits).mean()
        if self.label_smoothing > 0:
            loss = (1-self.label_smoothing)*loss + self.label_smoothing*(-F.logsigmoid(-self.beta*logits).mean())
        with torch.no_grad():
            rc = self.beta*(pi_c-ref_c); rr = self.beta*(pi_r-ref_r)
            acc = (rc > rr).float().mean()
        return loss, {"loss": loss.item(), "accuracy": acc.item(),
                      "reward_margin": (rc-rr).mean().item()}
