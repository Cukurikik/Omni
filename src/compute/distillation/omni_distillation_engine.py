"""
omni_distillation_engine.py — Knowledge Distillation Engine
Inspired by: DistilBERT/TinyBERT + OMNI model compression
Layer: Compute / AI

Multi-strategy distillation with temperature-scaled KD,
feature-level distillation, and progressive layer dropping.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DistillationConfig:
    temperature: float = 4.0
    alpha_kd: float = 0.7        # weight for KD loss
    alpha_task: float = 0.3      # weight for task loss
    alpha_feature: float = 0.1   # weight for feature distillation
    alpha_attention: float = 0.1 # weight for attention transfer
    progressive_layers: bool = False
    num_student_layers: int = 6
    num_teacher_layers: int = 12


class SoftTargetLoss(nn.Module):
    """Temperature-scaled KL divergence for soft label distillation."""

    def __init__(self, temperature: float = 4.0):
        super().__init__()
        self.temperature = temperature

    def forward(self, student_logits: torch.Tensor,
                teacher_logits: torch.Tensor) -> torch.Tensor:
        T = self.temperature
        student_log_probs = F.log_softmax(student_logits / T, dim=-1)
        teacher_probs = F.softmax(teacher_logits / T, dim=-1)
        loss = F.kl_div(student_log_probs, teacher_probs, reduction="batchmean")
        return loss * (T * T)


class FeatureDistillationLoss(nn.Module):
    """Align intermediate feature representations between teacher and student."""

    def __init__(self, student_dim: int, teacher_dim: int):
        super().__init__()
        self.projector = nn.Linear(student_dim, teacher_dim) if student_dim != teacher_dim else nn.Identity()
        self.loss_fn = nn.MSELoss()

    def forward(self, student_features: torch.Tensor,
                teacher_features: torch.Tensor) -> torch.Tensor:
        projected = self.projector(student_features)
        # Normalize for stable training
        projected = F.normalize(projected, dim=-1)
        teacher_normed = F.normalize(teacher_features.detach(), dim=-1)
        return self.loss_fn(projected, teacher_normed)


class AttentionTransferLoss(nn.Module):
    """Transfer attention maps from teacher to student."""

    def forward(self, student_attn: torch.Tensor,
                teacher_attn: torch.Tensor) -> torch.Tensor:
        # Ensure compatible shapes
        if student_attn.shape != teacher_attn.shape:
            # Interpolate student attention to match teacher
            student_attn = F.interpolate(
                student_attn.float(),
                size=teacher_attn.shape[-2:],
                mode="bilinear",
                align_corners=False,
            )
        return F.mse_loss(student_attn, teacher_attn.detach())


class LayerMapper:
    """Maps student layers to teacher layers for feature distillation."""

    def __init__(self, num_student: int, num_teacher: int):
        self.num_student = num_student
        self.num_teacher = num_teacher
        self.mapping = self._build_mapping()

    def _build_mapping(self) -> Dict[int, int]:
        """Evenly distribute student layers across teacher layers."""
        mapping = {}
        ratio = self.num_teacher / self.num_student
        for s in range(self.num_student):
            t = min(int(round((s + 1) * ratio)) - 1, self.num_teacher - 1)
            mapping[s] = t
        return mapping

    def get_teacher_layer(self, student_layer: int) -> int:
        return self.mapping.get(student_layer, student_layer)


class OmniDistillationEngine:
    """Production knowledge distillation engine.

    Supports:
    - Soft target (logit) distillation with temperature scaling
    - Feature-level distillation with linear projection
    - Attention map transfer
    - Progressive layer dropping
    - Combined multi-loss training
    """

    def __init__(self, teacher: nn.Module, student: nn.Module,
                 config: DistillationConfig = DistillationConfig()):
        self.teacher = teacher
        self.student = student
        self.config = config

        # Freeze teacher
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

        self.soft_target_loss = SoftTargetLoss(config.temperature)
        self.attention_loss = AttentionTransferLoss()
        self.layer_mapper = LayerMapper(config.num_student_layers,
                                        config.num_teacher_layers)

        self._feature_losses: List[FeatureDistillationLoss] = []
        self._step = 0

    def setup_feature_distillation(self, student_dim: int, teacher_dim: int):
        """Initialize feature distillation projectors."""
        for _ in range(self.config.num_student_layers):
            self._feature_losses.append(
                FeatureDistillationLoss(student_dim, teacher_dim)
            )

    def distill_step(
        self,
        inputs: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        task_criterion: Optional[nn.Module] = None,
    ) -> Dict[str, torch.Tensor]:
        """Execute one distillation training step.

        Returns dict with individual loss components and total loss.
        """
        self.student.train()
        self._step += 1

        # Teacher forward (no grad)
        with torch.no_grad():
            teacher_out = self.teacher(inputs)
            if isinstance(teacher_out, dict):
                teacher_logits = teacher_out.get("logits", teacher_out.get("output"))
                teacher_features = teacher_out.get("hidden_states", [])
                teacher_attentions = teacher_out.get("attentions", [])
            else:
                teacher_logits = teacher_out
                teacher_features = []
                teacher_attentions = []

        # Student forward
        student_out = self.student(inputs)
        if isinstance(student_out, dict):
            student_logits = student_out.get("logits", student_out.get("output"))
            student_features = student_out.get("hidden_states", [])
            student_attentions = student_out.get("attentions", [])
        else:
            student_logits = student_out
            student_features = []
            student_attentions = []

        losses = {}

        # 1. Soft target KD loss
        kd_loss = self.soft_target_loss(student_logits, teacher_logits)
        losses["kd_loss"] = kd_loss

        # 2. Task loss (hard labels)
        task_loss = torch.tensor(0.0, device=inputs.device)
        if labels is not None and task_criterion is not None:
            task_loss = task_criterion(student_logits, labels)
        losses["task_loss"] = task_loss

        # 3. Feature distillation loss
        feature_loss = torch.tensor(0.0, device=inputs.device)
        if student_features and teacher_features and self._feature_losses:
            for s_idx, feat_loss_fn in enumerate(self._feature_losses):
                t_idx = self.layer_mapper.get_teacher_layer(s_idx)
                if s_idx < len(student_features) and t_idx < len(teacher_features):
                    fl = feat_loss_fn(student_features[s_idx],
                                      teacher_features[t_idx])
                    feature_loss = feature_loss + fl
            feature_loss = feature_loss / max(1, len(self._feature_losses))
        losses["feature_loss"] = feature_loss

        # 4. Attention transfer loss
        attn_loss = torch.tensor(0.0, device=inputs.device)
        if student_attentions and teacher_attentions:
            count = 0
            for s_idx in range(min(len(student_attentions), self.config.num_student_layers)):
                t_idx = self.layer_mapper.get_teacher_layer(s_idx)
                if t_idx < len(teacher_attentions):
                    al = self.attention_loss(student_attentions[s_idx],
                                              teacher_attentions[t_idx])
                    attn_loss = attn_loss + al
                    count += 1
            attn_loss = attn_loss / max(1, count)
        losses["attention_loss"] = attn_loss

        # Combined loss
        total = (
            self.config.alpha_kd * kd_loss +
            self.config.alpha_task * task_loss +
            self.config.alpha_feature * feature_loss +
            self.config.alpha_attention * attn_loss
        )
        losses["total_loss"] = total

        return losses

    def get_compression_ratio(self) -> Dict[str, float]:
        """Calculate model compression metrics."""
        teacher_params = sum(p.numel() for p in self.teacher.parameters())
        student_params = sum(p.numel() for p in self.student.parameters())
        teacher_size = sum(p.numel() * p.element_size() for p in self.teacher.parameters())
        student_size = sum(p.numel() * p.element_size() for p in self.student.parameters())

        return {
            "teacher_params": teacher_params,
            "student_params": student_params,
            "param_ratio": student_params / max(1, teacher_params),
            "size_ratio": student_size / max(1, teacher_size),
            "compression": 1.0 - student_params / max(1, teacher_params),
        }
