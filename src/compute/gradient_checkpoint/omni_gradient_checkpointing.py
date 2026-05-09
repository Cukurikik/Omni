"""
omni_gradient_checkpointing.py — Memory-Efficient Gradient Checkpointing
Inspired by: Memformer/SoundStorm large model training
Layer: Compute / AI

Selective gradient checkpointing with automatic memory profiling
to minimize VRAM usage during training of large transformer models.
"""

import torch
import torch.nn as nn
from torch.utils.checkpoint import checkpoint
from typing import Optional, List, Tuple, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryProfile:
    layer_idx: int
    activation_bytes: int
    parameter_bytes: int
    should_checkpoint: bool


class SelectiveCheckpointer:
    """Automatically selects which layers to checkpoint based on memory budget.

    Profiles activation sizes per layer and checkpoints the largest ones
    until total memory fits within the VRAM budget.
    """

    def __init__(self, memory_budget_gb: float = 12.0,
                 min_checkpoint_layers: int = 0):
        self.memory_budget_bytes = int(memory_budget_gb * 1024**3)
        self.min_checkpoint_layers = min_checkpoint_layers
        self.profiles: List[MemoryProfile] = []
        self._profiled = False

    def profile_model(self, model: nn.Module, sample_input: torch.Tensor):
        """Profile each layer's activation memory consumption."""
        self.profiles = []

        hooks = []
        activation_sizes = {}

        def make_hook(idx):
            def hook_fn(module, input, output):
                if isinstance(output, torch.Tensor):
                    activation_sizes[idx] = output.nelement() * output.element_size()
                elif isinstance(output, tuple):
                    total = sum(
                        o.nelement() * o.element_size()
                        for o in output if isinstance(o, torch.Tensor)
                    )
                    activation_sizes[idx] = total
            return hook_fn

        for idx, (name, module) in enumerate(model.named_modules()):
            if isinstance(module, (nn.TransformerEncoderLayer,
                                   nn.TransformerDecoderLayer)):
                hooks.append(module.register_forward_hook(make_hook(idx)))

        with torch.no_grad():
            model(sample_input)

        for h in hooks:
            h.remove()

        total_activation_bytes = 0
        for idx, size in sorted(activation_sizes.items()):
            param_bytes = sum(p.nelement() * p.element_size()
                              for p in model.parameters())
            profile = MemoryProfile(
                layer_idx=idx,
                activation_bytes=size,
                parameter_bytes=param_bytes,
                should_checkpoint=False,
            )
            self.profiles.append(profile)
            total_activation_bytes += size

        # Mark layers for checkpointing (largest first)
        sorted_profiles = sorted(self.profiles,
                                 key=lambda p: p.activation_bytes, reverse=True)
        saved = 0
        needed = max(0, total_activation_bytes - self.memory_budget_bytes)

        for profile in sorted_profiles:
            if saved >= needed and len([p for p in self.profiles if p.should_checkpoint]) >= self.min_checkpoint_layers:
                break
            profile.should_checkpoint = True
            saved += profile.activation_bytes

        self._profiled = True
        logger.info(f"Profiled {len(self.profiles)} layers, "
                     f"checkpointing {sum(1 for p in self.profiles if p.should_checkpoint)}, "
                     f"saving ~{saved / 1024**2:.1f}MB")

    def get_checkpoint_indices(self) -> set:
        return {p.layer_idx for p in self.profiles if p.should_checkpoint}


class CheckpointedTransformerEncoder(nn.Module):
    """Transformer encoder with selective gradient checkpointing."""

    def __init__(self, dim: int = 768, depth: int = 12, heads: int = 12,
                 ff_mult: int = 4, dropout: float = 0.1,
                 checkpoint_every: int = 2):
        super().__init__()
        self.checkpoint_every = checkpoint_every
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=dim, nhead=heads,
                dim_feedforward=dim * ff_mult,
                dropout=dropout, activation="gelu",
                batch_first=True, norm_first=True,
            )
            for _ in range(depth)
        ])
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        for idx, layer in enumerate(self.layers):
            if self.training and (idx % self.checkpoint_every == 0):
                x = checkpoint(
                    self._layer_forward, layer, x, mask,
                    use_reentrant=False,
                )
            else:
                x = self._layer_forward(layer, x, mask)
        return self.norm(x)

    @staticmethod
    def _layer_forward(layer: nn.Module, x: torch.Tensor,
                       mask: Optional[torch.Tensor]) -> torch.Tensor:
        return layer(x, src_key_padding_mask=mask)


class GradientAccumulationManager:
    """Manages gradient accumulation with memory-aware stepping."""

    def __init__(self, model: nn.Module, optimizer: torch.optim.Optimizer,
                 accumulation_steps: int = 4, max_grad_norm: float = 1.0):
        self.model = model
        self.optimizer = optimizer
        self.accumulation_steps = accumulation_steps
        self.max_grad_norm = max_grad_norm
        self._step_count = 0

    def backward_step(self, loss: torch.Tensor) -> bool:
        """Backward pass with accumulation. Returns True if optimizer stepped."""
        scaled_loss = loss / self.accumulation_steps
        scaled_loss.backward()
        self._step_count += 1

        if self._step_count % self.accumulation_steps == 0:
            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.max_grad_norm
            )
            self.optimizer.step()
            self.optimizer.zero_grad()
            return True
        return False

    @property
    def should_step(self) -> bool:
        return self._step_count % self.accumulation_steps == 0

    @property
    def effective_step(self) -> int:
        return self._step_count // self.accumulation_steps
