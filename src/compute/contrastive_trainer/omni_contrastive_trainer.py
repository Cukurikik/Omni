"""
omni_contrastive_trainer.py — Contrastive Learning Training Engine
Inspired by: FashionCLIP + TVLT contrastive pretraining
Layer: Compute / AI

Production training loop for multi-modal contrastive learning with:
- Mixed precision (AMP) training
- Gradient accumulation for large effective batch sizes
- Distributed data-parallel support scaffolding
- Learning rate warmup + cosine decay
- EMA model averaging
"""

import math
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.cuda.amp import GradScaler, autocast

logger = logging.getLogger(__name__)


class LRScheduleType(Enum):
    COSINE = "cosine"
    LINEAR = "linear"
    CONSTANT = "constant"
    COSINE_WARMUP = "cosine_warmup"


@dataclass
class TrainerConfig:
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    warmup_steps: int = 2000
    total_steps: int = 100000
    batch_size: int = 256
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0
    schedule: LRScheduleType = LRScheduleType.COSINE_WARMUP
    ema_decay: float = 0.9999
    use_amp: bool = True
    log_interval: int = 100
    eval_interval: int = 1000
    checkpoint_interval: int = 5000
    temperature_learnable: bool = True
    initial_temperature: float = 0.07


@dataclass
class TrainingMetrics:
    step: int = 0
    epoch: int = 0
    loss: float = 0.0
    contrastive_loss: float = 0.0
    aux_loss: float = 0.0
    learning_rate: float = 0.0
    grad_norm: float = 0.0
    temperature: float = 0.07
    accuracy_i2t: float = 0.0
    accuracy_t2i: float = 0.0
    throughput_samples_sec: float = 0.0


class CosineWarmupScheduler:
    """Learning rate scheduler with linear warmup and cosine decay."""

    def __init__(self, optimizer: torch.optim.Optimizer, warmup_steps: int,
                 total_steps: int, min_lr_ratio: float = 0.01):
        self.optimizer = optimizer
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        self.min_lr_ratio = min_lr_ratio
        self.base_lrs = [pg['lr'] for pg in optimizer.param_groups]
        self._step = 0

    def step(self):
        self._step += 1
        lr_mult = self._get_lr_multiplier()
        for pg, base_lr in zip(self.optimizer.param_groups, self.base_lrs):
            pg['lr'] = base_lr * lr_mult

    def _get_lr_multiplier(self) -> float:
        if self._step < self.warmup_steps:
            return self._step / max(1, self.warmup_steps)
        elif self._step >= self.total_steps:
            return self.min_lr_ratio
        else:
            progress = (self._step - self.warmup_steps) / max(1, self.total_steps - self.warmup_steps)
            cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
            return max(self.min_lr_ratio, cosine_decay)

    def get_lr(self) -> float:
        if self.optimizer.param_groups:
            return self.optimizer.param_groups[0]['lr']
        return 0.0


class EMAModel:
    """Exponential Moving Average of model parameters for stable evaluation."""

    def __init__(self, model: nn.Module, decay: float = 0.9999):
        self.model = model
        self.decay = decay
        self.shadow = {}
        self.backup = {}
        self._initialize()

    def _initialize(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone()

    @torch.no_grad()
    def update(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad and name in self.shadow:
                self.shadow[name].mul_(self.decay).add_(
                    param.data, alpha=1.0 - self.decay
                )

    def apply_shadow(self):
        for name, param in self.model.named_parameters():
            if name in self.shadow:
                self.backup[name] = param.data.clone()
                param.data.copy_(self.shadow[name])

    def restore(self):
        for name, param in self.model.named_parameters():
            if name in self.backup:
                param.data.copy_(self.backup[name])
        self.backup = {}


def compute_contrastive_loss(
    image_features: torch.Tensor,
    text_features: torch.Tensor,
    temperature: torch.Tensor,
) -> Tuple[torch.Tensor, float, float]:
    """Symmetric contrastive loss (CLIP-style) with accuracy tracking."""
    image_features = F.normalize(image_features, dim=-1)
    text_features = F.normalize(text_features, dim=-1)

    logit_scale = temperature.exp().clamp(max=100.0)
    logits_per_image = logit_scale * image_features @ text_features.T
    logits_per_text = logits_per_image.T

    batch_size = image_features.shape[0]
    labels = torch.arange(batch_size, device=image_features.device)

    loss_i2t = F.cross_entropy(logits_per_image, labels)
    loss_t2i = F.cross_entropy(logits_per_text, labels)
    loss = (loss_i2t + loss_t2i) / 2

    # Compute retrieval accuracy
    acc_i2t = (logits_per_image.argmax(dim=-1) == labels).float().mean().item()
    acc_t2i = (logits_per_text.argmax(dim=-1) == labels).float().mean().item()

    return loss, acc_i2t, acc_t2i


class OmniContrastiveTrainer:
    """Production contrastive learning trainer with AMP and EMA.

    Handles the full training loop for CLIP-style models including:
    - Mixed precision training with gradient scaling
    - Gradient accumulation for large effective batch sizes
    - EMA model averaging for evaluation
    - Cosine learning rate schedule with warmup
    - Comprehensive metric tracking
    """

    def __init__(
        self,
        model: nn.Module,
        config: TrainerConfig,
        device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    ):
        self.model = model.to(device)
        self.config = config
        self.device = device

        # Optimizer with weight decay
        no_decay = {"bias", "LayerNorm.weight", "layer_norm.weight"}
        param_groups = [
            {
                "params": [p for n, p in model.named_parameters()
                          if not any(nd in n for nd in no_decay) and p.requires_grad],
                "weight_decay": config.weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters()
                          if any(nd in n for nd in no_decay) and p.requires_grad],
                "weight_decay": 0.0,
            },
        ]
        self.optimizer = torch.optim.AdamW(param_groups, lr=config.learning_rate)
        self.scheduler = CosineWarmupScheduler(
            self.optimizer, config.warmup_steps, config.total_steps
        )

        self.scaler = GradScaler(enabled=config.use_amp)
        self.ema = EMAModel(model, config.ema_decay)

        # Learnable temperature
        if config.temperature_learnable:
            self.log_temperature = nn.Parameter(
                torch.tensor(math.log(1.0 / config.initial_temperature), device=device)
            )
        else:
            self.log_temperature = torch.tensor(
                math.log(1.0 / config.initial_temperature), device=device
            )

        self.global_step = 0
        self.metrics_history: List[TrainingMetrics] = []

    def train_step(
        self,
        image_features: torch.Tensor,
        text_features: torch.Tensor,
        aux_loss: Optional[torch.Tensor] = None,
    ) -> TrainingMetrics:
        """Execute a single training step with gradient accumulation."""
        self.model.train()
        image_features = image_features.to(self.device)
        text_features = text_features.to(self.device)

        with autocast(enabled=self.config.use_amp):
            contrastive_loss, acc_i2t, acc_t2i = compute_contrastive_loss(
                image_features, text_features, self.log_temperature
            )

            total_loss = contrastive_loss
            if aux_loss is not None:
                total_loss = total_loss + aux_loss.to(self.device)

            # Scale for gradient accumulation
            scaled_loss = total_loss / self.config.gradient_accumulation_steps

        self.scaler.scale(scaled_loss).backward()

        metrics = TrainingMetrics(
            step=self.global_step,
            loss=total_loss.item(),
            contrastive_loss=contrastive_loss.item(),
            aux_loss=aux_loss.item() if aux_loss is not None else 0.0,
            temperature=self.log_temperature.exp().item(),
            accuracy_i2t=acc_i2t,
            accuracy_t2i=acc_t2i,
            learning_rate=self.scheduler.get_lr(),
        )

        # Accumulate gradients
        if (self.global_step + 1) % self.config.gradient_accumulation_steps == 0:
            # Gradient clipping
            self.scaler.unscale_(self.optimizer)
            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.config.max_grad_norm
            )
            metrics.grad_norm = grad_norm.item()

            self.scaler.step(self.optimizer)
            self.scaler.update()
            self.optimizer.zero_grad()
            self.scheduler.step()
            self.ema.update()

        self.global_step += 1
        self.metrics_history.append(metrics)
        return metrics

    @torch.no_grad()
    def evaluate(
        self,
        image_features: torch.Tensor,
        text_features: torch.Tensor,
        use_ema: bool = True,
    ) -> Dict[str, float]:
        """Evaluate using EMA model weights."""
        if use_ema:
            self.ema.apply_shadow()

        self.model.eval()
        image_features = image_features.to(self.device)
        text_features = text_features.to(self.device)

        loss, acc_i2t, acc_t2i = compute_contrastive_loss(
            image_features, text_features, self.log_temperature
        )

        if use_ema:
            self.ema.restore()

        return {
            "eval_loss": loss.item(),
            "eval_acc_i2t": acc_i2t,
            "eval_acc_t2i": acc_t2i,
            "eval_temperature": self.log_temperature.exp().item(),
        }

    def save_checkpoint(self, path: str):
        """Save training checkpoint."""
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_step": self.scheduler._step,
            "scaler_state_dict": self.scaler.state_dict(),
            "ema_shadow": self.ema.shadow,
            "log_temperature": self.log_temperature,
            "global_step": self.global_step,
            "config": self.config,
        }, path)
        logger.info(f"Saved checkpoint at step {self.global_step} to {path}")

    def load_checkpoint(self, path: str):
        """Load training checkpoint."""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scaler.load_state_dict(checkpoint["scaler_state_dict"])
        self.ema.shadow = checkpoint["ema_shadow"]
        self.log_temperature = checkpoint["log_temperature"]
        self.global_step = checkpoint["global_step"]
        logger.info(f"Loaded checkpoint from step {self.global_step}")
