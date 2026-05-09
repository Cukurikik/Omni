"""
OMNI Transformer — Training Pipeline
Production training loop with mixed precision, gradient accumulation,
learning rate scheduling, and checkpointing.
Learned from: gszfwsb/Data-Whisperer, Shekswess/tiny-reasoning-language-model
"""
from __future__ import annotations
import os
import time
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    output_dir: str = "./checkpoints"
    num_epochs: int = 3
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_steps: int = 500
    max_grad_norm: float = 1.0
    gradient_accumulation_steps: int = 1
    fp16: bool = True
    bf16: bool = False
    logging_steps: int = 100
    save_steps: int = 1000
    eval_steps: int = 500
    seed: int = 42
    dataloader_num_workers: int = 4
    lr_scheduler_type: str = "cosine"  # "cosine", "linear", "constant"
    max_steps: int = -1  # -1 means use num_epochs


class CosineWarmupScheduler:
    """Cosine LR scheduler with linear warmup."""
    def __init__(self, optimizer, warmup_steps: int, total_steps: int, min_lr: float = 0.0):
        self.optimizer = optimizer
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        self.min_lr = min_lr
        self.base_lrs = [pg["lr"] for pg in optimizer.param_groups]
        self.current_step = 0

    def step(self):
        self.current_step += 1
        lr = self._compute_lr()
        for pg in self.optimizer.param_groups:
            pg["lr"] = lr

    def _compute_lr(self) -> float:
        import math
        if self.current_step < self.warmup_steps:
            return self.base_lrs[0] * self.current_step / max(1, self.warmup_steps)
        progress = (self.current_step - self.warmup_steps) / max(1, self.total_steps - self.warmup_steps)
        return self.min_lr + 0.5 * (self.base_lrs[0] - self.min_lr) * (1 + math.cos(math.pi * progress))


class OmniTrainer:
    """Production training loop for transformer models."""
    def __init__(
        self, model: nn.Module, train_loader: DataLoader,
        eval_loader: Optional[DataLoader] = None,
        config: Optional[TrainingConfig] = None,
        compute_metrics: Optional[Callable] = None,
    ):
        self.model = model
        self.train_loader = train_loader
        self.eval_loader = eval_loader
        self.config = config or TrainingConfig()
        self.compute_metrics = compute_metrics

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.optimizer = self._create_optimizer()
        total_steps = self._compute_total_steps()
        self.scheduler = CosineWarmupScheduler(self.optimizer, self.config.warmup_steps, total_steps)
        self.scaler = GradScaler(enabled=self.config.fp16)

        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        self.global_step = 0
        self.best_eval_loss = float("inf")

    def _create_optimizer(self):
        no_decay = {"bias", "LayerNorm.weight", "layer_norm.weight", "norm.weight"}
        param_groups = [
            {"params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
             "weight_decay": self.config.weight_decay},
            {"params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)],
             "weight_decay": 0.0},
        ]
        return torch.optim.AdamW(param_groups, lr=self.config.learning_rate, betas=(0.9, 0.999), eps=1e-8)

    def _compute_total_steps(self) -> int:
        if self.config.max_steps > 0:
            return self.config.max_steps
        return len(self.train_loader) * self.config.num_epochs // self.config.gradient_accumulation_steps

    def train(self) -> Dict[str, Any]:
        logger.info(f"Training on {self.device}, config: {asdict(self.config)}")
        self.model.train()
        train_loss = 0.0
        start_time = time.time()

        for epoch in range(self.config.num_epochs):
            for step, batch in enumerate(self.train_loader):
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}

                with autocast(enabled=self.config.fp16, dtype=torch.bfloat16 if self.config.bf16 else torch.float16):
                    outputs = self.model(**batch)
                    loss = outputs["loss"] / self.config.gradient_accumulation_steps

                self.scaler.scale(loss).backward()
                train_loss += loss.item()

                if (step + 1) % self.config.gradient_accumulation_steps == 0:
                    self.scaler.unscale_(self.optimizer)
                    nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.optimizer.zero_grad(set_to_none=True)
                    self.scheduler.step()
                    self.global_step += 1

                    if self.global_step % self.config.logging_steps == 0:
                        avg_loss = train_loss / self.config.logging_steps
                        elapsed = time.time() - start_time
                        logger.info(f"Step {self.global_step} | Loss: {avg_loss:.4f} | LR: {self.scheduler._compute_lr():.2e} | Time: {elapsed:.1f}s")
                        train_loss = 0.0

                    if self.global_step % self.config.save_steps == 0:
                        self._save_checkpoint(f"checkpoint-{self.global_step}")

                    if self.eval_loader and self.global_step % self.config.eval_steps == 0:
                        eval_results = self.evaluate()
                        if eval_results["eval_loss"] < self.best_eval_loss:
                            self.best_eval_loss = eval_results["eval_loss"]
                            self._save_checkpoint("best")
                        self.model.train()

                    if 0 < self.config.max_steps <= self.global_step:
                        break
            if 0 < self.config.max_steps <= self.global_step:
                break

        self._save_checkpoint("final")
        return {"total_steps": self.global_step, "best_eval_loss": self.best_eval_loss}

    @torch.inference_mode()
    def evaluate(self) -> Dict[str, float]:
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        for batch in self.eval_loader:
            batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
            outputs = self.model(**batch)
            total_loss += outputs["loss"].item()
            num_batches += 1
        avg_loss = total_loss / max(num_batches, 1)
        logger.info(f"Eval Loss: {avg_loss:.4f}")
        return {"eval_loss": avg_loss}

    def _save_checkpoint(self, name: str) -> None:
        path = Path(self.config.output_dir) / name
        path.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path / "model.pt")
        torch.save(self.optimizer.state_dict(), path / "optimizer.pt")
        with open(path / "config.json", "w") as f:
            json.dump({"global_step": self.global_step, **asdict(self.config)}, f, indent=2)
        logger.info(f"Saved checkpoint: {path}")
