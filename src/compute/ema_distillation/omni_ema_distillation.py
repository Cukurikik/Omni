"""
omni_ema_distillation.py — EMA Self-Distillation Engine
Inspired by: BYOL/DINO + FashionCLIP teacher-student training
Layer: Compute / AI

Self-distillation using exponential moving average teacher
with asymmetric architecture (predictor on student only).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict
import copy


class OmniEMADistillation(nn.Module):
    """BYOL-style self-distillation with EMA teacher.

    Student learns by predicting the teacher's representations.
    Teacher is an EMA copy of the student, never directly trained.
    """

    def __init__(self, backbone: nn.Module, feature_dim: int = 256,
                 hidden_dim: int = 4096, ema_decay: float = 0.996):
        super().__init__()
        self.student_backbone = backbone
        self.teacher_backbone = copy.deepcopy(backbone)
        for p in self.teacher_backbone.parameters():
            p.requires_grad = False

        self.ema_decay = ema_decay

        self.student_projector = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, feature_dim),
        )
        self.student_predictor = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, feature_dim),
        )
        self.teacher_projector = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, feature_dim),
        )

    @torch.no_grad()
    def update_teacher(self):
        """Update teacher parameters using EMA."""
        for sp, tp in zip(self.student_backbone.parameters(),
                          self.teacher_backbone.parameters()):
            tp.data.mul_(self.ema_decay).add_(sp.data, alpha=1.0 - self.ema_decay)

        for sp, tp in zip(self.student_projector.parameters(),
                          self.teacher_projector.parameters()):
            tp.data.mul_(self.ema_decay).add_(sp.data, alpha=1.0 - self.ema_decay)

    def _loss_fn(self, student_pred: torch.Tensor,
                 teacher_target: torch.Tensor) -> torch.Tensor:
        student_pred = F.normalize(student_pred, dim=-1)
        teacher_target = F.normalize(teacher_target, dim=-1)
        return 2.0 - 2.0 * (student_pred * teacher_target).sum(dim=-1).mean()

    def forward(self, view1: torch.Tensor,
                view2: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Student forward on both views
        s1 = self.student_predictor(self.student_projector(self.student_backbone(view1)))
        s2 = self.student_predictor(self.student_projector(self.student_backbone(view2)))

        # Teacher forward (no gradients)
        with torch.no_grad():
            t1 = self.teacher_projector(self.teacher_backbone(view1))
            t2 = self.teacher_projector(self.teacher_backbone(view2))

        # Symmetric loss
        loss = (self._loss_fn(s1, t2.detach()) + self._loss_fn(s2, t1.detach())) / 2.0

        return {
            "loss": loss,
            "student_repr": s1.detach(),
            "teacher_repr": t1.detach(),
        }
