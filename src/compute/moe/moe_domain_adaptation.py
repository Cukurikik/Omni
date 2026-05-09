"""
moe_domain_adaptation.py — MoE for Open Set Domain Adaptation
Reference: ZhenbangDu/DSD (Dual-Space Detection with MoE)
Layer: Compute / AI — Domain Adaptation

Uses Mixture of Experts with dual-space detection for open-set domain
adaptation. Each expert specializes in different domain characteristics,
and a GNN-based router detects out-of-distribution samples.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class DSDConfig:
    feature_dim: int = 2048
    num_experts: int = 4
    num_classes: int = 65
    ood_threshold: float = 0.5
    prototype_momentum: float = 0.99
    temperature: float = 0.07
    lambda_ood: float = 0.5


class DomainExpert(nn.Module):
    """Expert specializing in a specific domain characteristic."""
    def __init__(self, in_dim, out_dim, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, in_dim // 2),
            nn.BatchNorm1d(in_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(in_dim // 2, out_dim),
        )

    def forward(self, x):
        return self.net(x)


class PrototypeMemory(nn.Module):
    """Maintains class prototypes for open-set detection."""
    def __init__(self, num_classes, dim, momentum=0.99):
        super().__init__()
        self.num_classes = num_classes
        self.momentum = momentum
        self.register_buffer("prototypes", torch.randn(num_classes, dim))
        self.register_buffer("counts", torch.zeros(num_classes))

    @torch.no_grad()
    def update(self, features, labels):
        for c in range(self.num_classes):
            mask = labels == c
            if mask.any():
                new_proto = features[mask].mean(dim=0)
                if self.counts[c] == 0:
                    self.prototypes[c] = new_proto
                else:
                    self.prototypes[c] = (self.momentum * self.prototypes[c] +
                                          (1 - self.momentum) * new_proto)
                self.counts[c] += mask.sum()

    def compute_distances(self, features):
        """Compute cosine distance to each prototype."""
        features_norm = F.normalize(features, dim=-1)
        proto_norm = F.normalize(self.prototypes, dim=-1)
        return torch.mm(features_norm, proto_norm.T)


class DualSpaceDetector(nn.Module):
    """Detects OOD samples using feature + prediction space analysis."""
    def __init__(self, config: DSDConfig):
        super().__init__()
        self.config = config
        self.feature_scorer = nn.Sequential(
            nn.Linear(config.feature_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )
        self.prototype_mem = PrototypeMemory(
            config.num_classes, config.feature_dim, config.prototype_momentum)

    def forward(self, features, logits=None):
        # Feature-space OOD score
        feat_score = self.feature_scorer(features).squeeze(-1)

        # Prediction-space OOD score: entropy of softmax
        if logits is not None:
            probs = F.softmax(logits, dim=-1)
            entropy = -(probs * (probs + 1e-8).log()).sum(dim=-1)
            max_entropy = torch.log(torch.tensor(float(logits.shape[-1])))
            pred_score = entropy / max_entropy
        else:
            pred_score = torch.zeros_like(feat_score)

        # Prototype-space score: max similarity to known prototypes
        proto_sim = self.prototype_mem.compute_distances(features)
        proto_score = 1.0 - proto_sim.max(dim=-1).values

        # Combined OOD score
        ood_score = (feat_score + pred_score + proto_score) / 3.0
        is_ood = ood_score > self.config.ood_threshold

        return ood_score, is_ood


class MoEDomainAdapter(nn.Module):
    """Full MoE-based domain adaptation with open-set detection.

    Architecture:
    - Shared backbone encoder
    - Per-domain expert branches
    - Dual-space OOD detector
    - Gating network for expert selection
    """
    def __init__(self, backbone: nn.Module, config: DSDConfig):
        super().__init__()
        self.backbone = backbone
        self.config = config

        self.experts = nn.ModuleList([
            DomainExpert(config.feature_dim, config.num_classes)
            for _ in range(config.num_experts)])
        self.gate = nn.Linear(config.feature_dim, config.num_experts)
        self.ood_detector = DualSpaceDetector(config)
        self.projection = nn.Sequential(
            nn.Linear(config.feature_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128))

    def forward(self, x, labels=None):
        features = self.backbone(x)
        if features.dim() > 2:
            features = features.mean(dim=list(range(2, features.dim())))

        # Expert routing
        gate_logits = self.gate(features)
        gate_probs = F.softmax(gate_logits, dim=-1)

        # Aggregate expert predictions
        all_logits = torch.stack([e(features) for e in self.experts], dim=1)
        logits = (all_logits * gate_probs.unsqueeze(-1)).sum(dim=1)

        # OOD detection
        ood_score, is_ood = self.ood_detector(features, logits)

        result = {
            "logits": logits,
            "features": features,
            "ood_score": ood_score,
            "is_ood": is_ood,
            "gate_probs": gate_probs,
        }

        if labels is not None:
            # Classification loss (only known classes)
            known_mask = labels < self.config.num_classes
            if known_mask.any():
                cls_loss = F.cross_entropy(logits[known_mask], labels[known_mask])
            else:
                cls_loss = torch.tensor(0.0, device=x.device)

            # OOD detection loss
            ood_labels = (~known_mask).float()
            ood_loss = F.binary_cross_entropy(ood_score, ood_labels)

            # Load balance loss for expert utilization
            expert_usage = gate_probs.mean(dim=0)
            lb_loss = (expert_usage * torch.log(expert_usage + 1e-8)).sum()

            # Contrastive loss for feature alignment
            proj = F.normalize(self.projection(features), dim=-1)
            contrastive = self._contrastive_loss(proj, labels, known_mask)

            result["loss"] = cls_loss + self.config.lambda_ood * ood_loss - 0.01 * lb_loss + contrastive
            result["cls_loss"] = cls_loss
            result["ood_loss"] = ood_loss

            # Update prototypes
            if known_mask.any():
                self.ood_detector.prototype_mem.update(
                    features[known_mask].detach(), labels[known_mask])

        return result

    def _contrastive_loss(self, proj, labels, known_mask):
        """Supervised contrastive loss for known-class feature alignment."""
        if not known_mask.any() or known_mask.sum() < 2:
            return torch.tensor(0.0, device=proj.device)

        proj_known = proj[known_mask]
        labels_known = labels[known_mask]

        sim = torch.mm(proj_known, proj_known.T) / self.config.temperature
        sim.fill_diagonal_(float("-inf"))

        pos_mask = labels_known.unsqueeze(0) == labels_known.unsqueeze(1)
        pos_mask.fill_diagonal_(False)

        if not pos_mask.any():
            return torch.tensor(0.0, device=proj.device)

        exp_sim = torch.exp(sim)
        log_prob = sim - torch.log(exp_sim.sum(dim=1, keepdim=True) + 1e-8)
        loss = -(log_prob * pos_mask.float()).sum() / pos_mask.float().sum().clamp(min=1)
        return loss * 0.1
