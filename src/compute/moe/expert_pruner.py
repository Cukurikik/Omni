"""
expert_pruner.py — Expert Pruning and Compression for MoE Models
Reference: optimal-sparsity, expert-pruning literature
Layer: Compute / AI — MoE Optimization

Prunes underutilized experts from MoE models based on usage statistics,
gradient sensitivity, and knowledge distillation. Reduces model size
while maintaining accuracy through selective expert removal.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PruneConfig:
    prune_ratio: float = 0.25
    method: str = "usage"  # usage, sensitivity, combined
    calibration_batches: int = 100
    distill_temperature: float = 4.0
    distill_alpha: float = 0.5
    min_experts: int = 2
    sensitivity_samples: int = 32


class ExpertUsageTracker:
    """Tracks expert utilization across training/inference."""
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        self.total_tokens = 0
        self.expert_tokens = torch.zeros(num_experts)
        self.expert_weight_sum = torch.zeros(num_experts)
        self.batches_seen = 0

    @torch.no_grad()
    def update(self, indices: torch.Tensor, weights: torch.Tensor):
        N = indices.shape[0]
        self.total_tokens += N
        self.batches_seen += 1
        for k in range(indices.shape[1]):
            for e in range(self.num_experts):
                mask = indices[:, k] == e
                self.expert_tokens[e] += mask.sum().item()
                if mask.any():
                    self.expert_weight_sum[e] += weights[mask, k].sum().item()

    def get_usage_scores(self) -> torch.Tensor:
        if self.total_tokens == 0:
            return torch.ones(self.num_experts)
        return self.expert_tokens / max(self.total_tokens, 1)

    def get_importance_scores(self) -> torch.Tensor:
        if self.total_tokens == 0:
            return torch.ones(self.num_experts)
        usage = self.get_usage_scores()
        avg_weight = self.expert_weight_sum / self.expert_tokens.clamp(min=1)
        return usage * avg_weight


class GradientSensitivityAnalyzer:
    """Analyzes expert importance via gradient-based sensitivity."""
    def __init__(self, model, num_experts):
        self.model = model
        self.num_experts = num_experts

    @torch.no_grad()
    def compute_sensitivity(self, data_loader, num_batches=32):
        """Fisher Information based sensitivity per expert."""
        sensitivities = torch.zeros(self.num_experts)
        self.model.eval()

        batch_count = 0
        for batch in data_loader:
            if batch_count >= num_batches:
                break
            self.model.zero_grad()

            with torch.enable_grad():
                input_ids = batch["input_ids"]
                output = self.model(input_ids)
                logits = output["logits"] if isinstance(output, dict) else output
                probs = F.softmax(logits[:, -1], dim=-1)
                # Sample from output distribution
                sampled = torch.multinomial(probs, 1).squeeze(-1)
                loss = F.cross_entropy(logits[:, -1], sampled)
                loss.backward()

            # Accumulate gradient magnitudes per expert
            for name, param in self.model.named_parameters():
                if param.grad is not None and "expert" in name:
                    # Parse expert index from parameter name
                    for e in range(self.num_experts):
                        if f"experts.{e}." in name or f"expert_{e}." in name:
                            sensitivities[e] += param.grad.abs().sum().item()
                            break

            batch_count += 1

        return sensitivities / max(batch_count, 1)


class ExpertDistiller:
    """Distills knowledge from pruned experts into remaining ones."""
    def __init__(self, temperature=4.0, alpha=0.5):
        self.temperature = temperature
        self.alpha = alpha

    def distill_step(self, teacher_model, student_model, batch):
        """Single distillation step: student learns from teacher."""
        student_model.train()
        teacher_model.eval()

        with torch.no_grad():
            teacher_out = teacher_model(batch["input_ids"])
            teacher_logits = teacher_out["logits"] if isinstance(teacher_out, dict) \
                else teacher_out

        student_out = student_model(batch["input_ids"])
        student_logits = student_out["logits"] if isinstance(student_out, dict) \
            else student_out

        # KD loss: KL divergence on softened probabilities
        T = self.temperature
        teacher_soft = F.log_softmax(teacher_logits / T, dim=-1)
        student_soft = F.log_softmax(student_logits / T, dim=-1)
        kd_loss = F.kl_div(student_soft, teacher_soft.exp(), reduction="batchmean") * (T ** 2)

        # Hard label loss
        labels = batch.get("labels", batch["input_ids"][:, 1:])
        hard_loss = F.cross_entropy(
            student_logits[:, :-1].reshape(-1, student_logits.shape[-1]),
            labels.reshape(-1), ignore_index=-100)

        # Combined loss
        aux_loss = student_out.get("aux_loss", torch.tensor(0.0)) \
            if isinstance(student_out, dict) else torch.tensor(0.0)
        total_loss = self.alpha * kd_loss + (1 - self.alpha) * hard_loss + aux_loss

        return total_loss, {"kd_loss": kd_loss.item(), "hard_loss": hard_loss.item()}


class ExpertPruner:
    """Prunes experts from MoE models based on importance scores."""
    def __init__(self, config: PruneConfig):
        self.config = config

    def compute_scores(self, model, data_loader=None) -> torch.Tensor:
        """Compute importance scores for each expert."""
        # Find MoE layers and extract expert count
        num_experts = self._get_num_experts(model)
        if num_experts is None:
            raise ValueError("Could not find MoE layers in model")

        tracker = ExpertUsageTracker(num_experts)

        if data_loader is not None and self.config.method in ("usage", "combined"):
            model.eval()
            batch_count = 0
            for batch in data_loader:
                if batch_count >= self.config.calibration_batches:
                    break
                with torch.no_grad():
                    # Hook into router to track usage
                    output = model(batch["input_ids"])
                batch_count += 1

        usage_scores = tracker.get_importance_scores()

        if self.config.method == "sensitivity" and data_loader is not None:
            analyzer = GradientSensitivityAnalyzer(model, num_experts)
            sens_scores = analyzer.compute_sensitivity(
                data_loader, self.config.sensitivity_samples)
            return sens_scores
        elif self.config.method == "combined" and data_loader is not None:
            analyzer = GradientSensitivityAnalyzer(model, num_experts)
            sens_scores = analyzer.compute_sensitivity(
                data_loader, self.config.sensitivity_samples)
            return 0.5 * usage_scores + 0.5 * sens_scores
        return usage_scores

    def prune(self, model, scores: torch.Tensor) -> Tuple[nn.Module, List[int]]:
        """Remove lowest-scoring experts from the model."""
        num_experts = len(scores)
        num_to_keep = max(
            self.config.min_experts,
            int(num_experts * (1 - self.config.prune_ratio)))
        num_to_prune = num_experts - num_to_keep

        sorted_idx = scores.argsort()
        pruned_idx = sorted_idx[:num_to_prune].tolist()
        kept_idx = sorted_idx[num_to_prune:].tolist()

        logger.info(
            f"Pruning {num_to_prune}/{num_experts} experts. "
            f"Keeping: {kept_idx}, Pruning: {pruned_idx}")

        # Remove experts from MoE layers
        for name, module in model.named_modules():
            if hasattr(module, 'experts') and isinstance(module.experts, nn.ModuleList):
                new_experts = nn.ModuleList([
                    module.experts[i] for i in kept_idx])
                module.experts = new_experts

                # Resize router
                if hasattr(module, 'router') and hasattr(module.router, 'gate'):
                    old_gate = module.router.gate
                    new_gate = nn.Linear(old_gate.in_features, num_to_keep, bias=False)
                    new_gate.weight.data = old_gate.weight.data[kept_idx]
                    module.router.gate = new_gate
                    module.router.num_experts = num_to_keep

                if hasattr(module, 'num_experts'):
                    module.num_experts = num_to_keep

        logger.info(f"Pruning complete. Model now has {num_to_keep} experts")
        return model, pruned_idx

    def _get_num_experts(self, model) -> Optional[int]:
        for module in model.modules():
            if hasattr(module, 'experts') and isinstance(module.experts, nn.ModuleList):
                return len(module.experts)
        return None
