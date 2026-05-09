"""
moe_knowledge_distillation.py — Teacher-Student MoE Distillation
Layer: Compute / AI — MoE Compression

Distills a large MoE teacher into a smaller student model:
- Expert-level distillation (per-expert KD)
- Router distillation (routing distribution matching)
- Feature-level distillation (intermediate representations)
- Progressive distillation with scheduled complexity
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DistillConfig:
    temperature: float = 4.0
    alpha_kd: float = 0.7
    alpha_task: float = 0.3
    alpha_router: float = 0.1
    alpha_feature: float = 0.05
    progressive: bool = True
    warmup_steps: int = 500
    feature_layers: List[int] = None

    def __post_init__(self):
        if self.feature_layers is None:
            self.feature_layers = []


class RouterDistillLoss(nn.Module):
    """KL divergence between teacher and student routing distributions."""
    def __init__(self, temperature=2.0):
        super().__init__()
        self.temperature = temperature

    def forward(self, student_logits, teacher_logits):
        student_probs = F.log_softmax(student_logits / self.temperature, dim=-1)
        teacher_probs = F.softmax(teacher_logits / self.temperature, dim=-1)
        loss = F.kl_div(student_probs, teacher_probs, reduction="batchmean")
        return loss * (self.temperature ** 2)


class FeatureDistillLoss(nn.Module):
    """MSE loss on intermediate feature representations."""
    def __init__(self, teacher_dim, student_dim):
        super().__init__()
        if teacher_dim != student_dim:
            self.projector = nn.Linear(student_dim, teacher_dim, bias=False)
        else:
            self.projector = nn.Identity()

    def forward(self, student_features, teacher_features):
        projected = self.projector(student_features)
        return F.mse_loss(projected, teacher_features.detach())


class ExpertDistillLoss(nn.Module):
    """Per-expert output distillation."""
    def __init__(self, temperature=2.0):
        super().__init__()
        self.temperature = temperature

    def forward(self, student_expert_outs, teacher_expert_outs):
        total_loss = torch.tensor(0.0, device=student_expert_outs[0].device)
        count = 0
        for s_out, t_out in zip(student_expert_outs, teacher_expert_outs):
            if s_out is not None and t_out is not None:
                loss = F.mse_loss(s_out, t_out.detach())
                total_loss = total_loss + loss
                count += 1
        return total_loss / max(count, 1)


class MoEDistiller:
    """Orchestrates MoE knowledge distillation."""
    def __init__(
        self,
        teacher: nn.Module,
        student: nn.Module,
        config: DistillConfig,
    ):
        self.teacher = teacher
        self.student = student
        self.config = config
        self.router_loss_fn = RouterDistillLoss(config.temperature)
        self.step = 0

        # Freeze teacher
        for p in self.teacher.parameters():
            p.requires_grad = False
        self.teacher.eval()

    def compute_loss(
        self,
        input_ids: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """Compute combined distillation loss."""
        # Teacher forward (no grad)
        with torch.no_grad():
            teacher_out = self.teacher(input_ids)
            t_logits = teacher_out["logits"] if isinstance(teacher_out, dict) else teacher_out

        # Student forward
        student_out = self.student(input_ids)
        s_logits = student_out["logits"] if isinstance(student_out, dict) else student_out

        # Output KD loss
        T = self.config.temperature
        kd_loss = F.kl_div(
            F.log_softmax(s_logits / T, dim=-1),
            F.softmax(t_logits / T, dim=-1),
            reduction="batchmean",
        ) * (T ** 2)

        # Task loss (if labels provided)
        task_loss = torch.tensor(0.0, device=s_logits.device)
        if labels is not None:
            task_loss = F.cross_entropy(
                s_logits.reshape(-1, s_logits.shape[-1]),
                labels.reshape(-1), ignore_index=-100)

        # Router distillation loss
        router_loss = torch.tensor(0.0, device=s_logits.device)
        if isinstance(teacher_out, dict) and isinstance(student_out, dict):
            t_router = teacher_out.get("router_logits")
            s_router = student_out.get("router_logits")
            if t_router is not None and s_router is not None:
                # Handle different number of experts
                min_e = min(t_router.shape[-1], s_router.shape[-1])
                router_loss = self.router_loss_fn(
                    s_router[..., :min_e], t_router[..., :min_e])

        # Progressive weighting
        alpha_kd, alpha_task = self._get_weights()

        total = (alpha_kd * kd_loss +
                 alpha_task * task_loss +
                 self.config.alpha_router * router_loss)

        if isinstance(student_out, dict) and "aux_loss" in student_out:
            total = total + student_out["aux_loss"]

        self.step += 1

        return {
            "loss": total,
            "kd_loss": kd_loss.item(),
            "task_loss": task_loss.item(),
            "router_loss": router_loss.item(),
        }

    def _get_weights(self) -> Tuple[float, float]:
        """Progressive: start with more KD, shift to more task loss."""
        if not self.config.progressive:
            return self.config.alpha_kd, self.config.alpha_task

        progress = min(1.0, self.step / max(self.config.warmup_steps, 1))
        alpha_kd = self.config.alpha_kd * (1 - 0.3 * progress)
        alpha_task = self.config.alpha_task + 0.3 * progress * self.config.alpha_kd
        return alpha_kd, alpha_task


class MoEToMoEDistiller(MoEDistiller):
    """Specialized distiller for MoE-to-MoE (e.g., 64 experts -> 8 experts)."""
    def __init__(self, teacher, student, config):
        super().__init__(teacher, student, config)
        self.expert_loss_fn = ExpertDistillLoss(config.temperature)

    def compute_expert_mapping(self) -> Dict[int, List[int]]:
        """Map student experts to teacher experts (many-to-one)."""
        t_num = self._count_experts(self.teacher)
        s_num = self._count_experts(self.student)
        ratio = max(1, t_num // s_num)

        mapping = {}
        for s_id in range(s_num):
            mapping[s_id] = list(range(s_id * ratio, min((s_id + 1) * ratio, t_num)))
        return mapping

    def _count_experts(self, model: nn.Module) -> int:
        for m in model.modules():
            if hasattr(m, 'experts') and isinstance(m.experts, nn.ModuleList):
                return len(m.experts)
        return 1
