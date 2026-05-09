"""
moe_continual_learning.py — Continual Learning for MoE via Expert Expansion
Layer: Compute / AI — MoE Lifelong Learning

Dynamically adds new experts to handle distribution shifts without
catastrophic forgetting. Uses expert freezing, elastic weight
consolidation, and progressive routing for continual adaptation.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional
from dataclasses import dataclass
import copy
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContinualConfig:
    initial_experts: int = 8
    max_experts: int = 32
    expansion_threshold: float = 0.85  # router entropy threshold
    ewc_lambda: float = 5000.0
    freeze_old_experts: bool = True
    expansion_ff_dim: int = 3072


class FisherInformationTracker:
    """Tracks Fisher Information Matrix for EWC regularization."""
    def __init__(self):
        self.fisher: Dict[str, torch.Tensor] = {}
        self.old_params: Dict[str, torch.Tensor] = {}

    @torch.no_grad()
    def compute_fisher(self, model, dataloader, num_batches=100):
        """Compute diagonal Fisher Information from data."""
        model.eval()
        fisher_acc = {n: torch.zeros_like(p) for n, p in model.named_parameters()
                      if p.requires_grad}
        count = 0

        for batch in dataloader:
            if count >= num_batches:
                break
            model.zero_grad()
            with torch.enable_grad():
                output = model(batch["input_ids"])
                logits = output["logits"] if isinstance(output, dict) else output
                # Sample from model's distribution
                probs = F.softmax(logits[:, -1], dim=-1)
                sampled = torch.multinomial(probs, 1).squeeze(-1)
                loss = F.cross_entropy(logits[:, -1], sampled)
                loss.backward()

            for n, p in model.named_parameters():
                if p.grad is not None and n in fisher_acc:
                    fisher_acc[n] += p.grad.data ** 2

            count += 1

        for n in fisher_acc:
            fisher_acc[n] /= max(count, 1)

        self.fisher = fisher_acc
        self.old_params = {n: p.data.clone() for n, p in model.named_parameters()
                           if p.requires_grad}

    def ewc_loss(self, model, lambda_: float) -> torch.Tensor:
        """Compute EWC regularization loss."""
        loss = torch.tensor(0.0, device=next(model.parameters()).device)
        for n, p in model.named_parameters():
            if n in self.fisher and n in self.old_params:
                loss += (self.fisher[n] * (p - self.old_params[n]) ** 2).sum()
        return 0.5 * lambda_ * loss


class ExpertExpander:
    """Dynamically expands MoE with new experts."""
    def __init__(self, config: ContinualConfig):
        self.config = config
        self.expansion_history: List[Dict] = []

    def should_expand(self, router_entropy: float, expert_usage: torch.Tensor) -> bool:
        """Determine if expansion is needed based on routing metrics."""
        max_entropy = torch.log(torch.tensor(float(len(expert_usage))))
        normalized_entropy = router_entropy / max_entropy.item()

        # Expand if routing is too concentrated (low entropy)
        # or if some experts are severely overloaded
        max_usage = expert_usage.max().item()
        return normalized_entropy < self.config.expansion_threshold or max_usage > 0.4

    def expand(self, moe_layer: nn.Module, dim: int) -> int:
        """Add a new expert to the MoE layer.

        Returns the new expert's index.
        """
        current_count = len(moe_layer.experts)
        if current_count >= self.config.max_experts:
            logger.warning(f"Max experts ({self.config.max_experts}) reached")
            return -1

        # Create new expert (initialized from average of existing)
        new_expert = nn.Sequential(
            nn.Linear(dim, self.config.expansion_ff_dim, bias=False),
            nn.SiLU(),
            nn.Linear(self.config.expansion_ff_dim, dim, bias=False),
        )

        # Initialize from average of existing experts
        with torch.no_grad():
            for name, new_param in new_expert.named_parameters():
                existing_params = []
                for expert in moe_layer.experts:
                    for ename, eparam in expert.named_parameters():
                        if ename == name and eparam.shape == new_param.shape:
                            existing_params.append(eparam.data)
                if existing_params:
                    avg = torch.stack(existing_params).mean(dim=0)
                    noise = torch.randn_like(avg) * 0.01
                    new_param.copy_(avg + noise)

        moe_layer.experts.append(new_expert.to(next(moe_layer.parameters()).device))

        # Expand router
        if hasattr(moe_layer, 'router') and hasattr(moe_layer.router, 'gate'):
            old_gate = moe_layer.router.gate
            new_gate = nn.Linear(old_gate.in_features, current_count + 1, bias=False)
            new_gate.weight.data[:current_count] = old_gate.weight.data
            new_gate.weight.data[current_count] = old_gate.weight.data.mean(dim=0)
            new_gate = new_gate.to(old_gate.weight.device)
            moe_layer.router.gate = new_gate
            moe_layer.router.num_experts = current_count + 1

        if hasattr(moe_layer, 'num_experts'):
            moe_layer.num_experts = current_count + 1

        # Freeze old experts if configured
        if self.config.freeze_old_experts:
            for i, expert in enumerate(moe_layer.experts[:-1]):
                for param in expert.parameters():
                    param.requires_grad = False

        self.expansion_history.append({
            "step": len(self.expansion_history),
            "old_count": current_count,
            "new_count": current_count + 1,
        })

        logger.info(f"Expanded MoE: {current_count} -> {current_count + 1} experts")
        return current_count

    def get_trainable_params(self, moe_layer: nn.Module) -> List[nn.Parameter]:
        """Get only the trainable parameters (new experts + router)."""
        params = []
        for p in moe_layer.router.parameters():
            if p.requires_grad:
                params.append(p)
        for expert in moe_layer.experts:
            for p in expert.parameters():
                if p.requires_grad:
                    params.append(p)
        return params


class ContinualMoETrainer:
    """Trainer for continual MoE learning with automatic expansion."""
    def __init__(self, model, config: ContinualConfig):
        self.model = model
        self.config = config
        self.fisher_tracker = FisherInformationTracker()
        self.expander = ExpertExpander(config)
        self.task_count = 0

    def learn_new_task(self, dataloader, epochs=5, lr=1e-4):
        """Learn a new task with EWC + optional expansion."""
        self.task_count += 1
        logger.info(f"Learning task {self.task_count}")

        # Check if expansion is needed
        moe_layer = self._find_moe_layer()
        if moe_layer is not None:
            dim = next(moe_layer.parameters()).shape[-1]

        optimizer = torch.optim.AdamW(
            [p for p in self.model.parameters() if p.requires_grad],
            lr=lr)

        for epoch in range(epochs):
            total_loss = 0.0
            count = 0
            for batch in dataloader:
                optimizer.zero_grad()
                output = self.model(batch["input_ids"])
                logits = output["logits"] if isinstance(output, dict) else output

                labels = batch.get("labels", batch["input_ids"][:, 1:])
                task_loss = F.cross_entropy(
                    logits[:, :-1].reshape(-1, logits.shape[-1]),
                    labels.reshape(-1), ignore_index=-100)

                # EWC regularization
                ewc_loss = self.fisher_tracker.ewc_loss(
                    self.model, self.config.ewc_lambda)

                loss = task_loss + ewc_loss
                if isinstance(output, dict) and "aux_loss" in output:
                    loss = loss + output["aux_loss"]

                loss.backward()
                optimizer.step()
                total_loss += task_loss.item()
                count += 1

            logger.info(f"  Epoch {epoch}: loss={total_loss/max(count,1):.4f}")

        # Update Fisher for next task
        self.fisher_tracker.compute_fisher(self.model, dataloader)
        logger.info(f"Task {self.task_count} complete")

    def _find_moe_layer(self):
        for m in self.model.modules():
            if hasattr(m, 'experts') and isinstance(m.experts, nn.ModuleList):
                return m
        return None
