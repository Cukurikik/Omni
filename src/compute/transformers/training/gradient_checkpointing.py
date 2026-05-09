"""
OMNI Transformer — Gradient Checkpointing Utilities
Memory-efficient training via activation recomputation.
"""
import torch
import torch.nn as nn
from torch.utils.checkpoint import checkpoint
from typing import List, Callable
import logging

logger = logging.getLogger(__name__)


class CheckpointedSequential(nn.Module):
    """Sequential module with gradient checkpointing support."""
    def __init__(self, layers: List[nn.Module], checkpoint_every: int = 1):
        super().__init__()
        self.layers = nn.ModuleList(layers)
        self.checkpoint_every = checkpoint_every

    def forward(self, x: torch.Tensor, **kwargs) -> torch.Tensor:
        for i, layer in enumerate(self.layers):
            if self.training and i % self.checkpoint_every == 0:
                x = checkpoint(self._run_layer, layer, x, use_reentrant=False)
            else:
                x = layer(x, **kwargs) if kwargs else layer(x)
        return x

    @staticmethod
    def _run_layer(layer: nn.Module, x: torch.Tensor) -> torch.Tensor:
        return layer(x)


def enable_gradient_checkpointing(model: nn.Module, target_class=None) -> int:
    """Enable gradient checkpointing on target layers."""
    count = 0
    for module in model.modules():
        if target_class and isinstance(module, target_class):
            module.gradient_checkpointing = True
            count += 1
        elif hasattr(module, 'gradient_checkpointing'):
            module.gradient_checkpointing = True
            count += 1
    logger.info(f"Enabled gradient checkpointing on {count} modules")
    return count


class MemoryTracker:
    """Track GPU memory usage during training."""
    def __init__(self):
        self.snapshots = []

    def snapshot(self, label: str = "") -> dict:
        if not torch.cuda.is_available():
            return {"label": label, "allocated_mb": 0, "reserved_mb": 0}
        info = {
            "label": label,
            "allocated_mb": round(torch.cuda.memory_allocated() / 1e6, 1),
            "reserved_mb": round(torch.cuda.memory_reserved() / 1e6, 1),
            "max_allocated_mb": round(torch.cuda.max_memory_allocated() / 1e6, 1),
        }
        self.snapshots.append(info)
        return info

    def reset_peak(self) -> None:
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

    def report(self) -> str:
        lines = ["Memory Report:"]
        for s in self.snapshots:
            lines.append(f"  {s['label']}: {s['allocated_mb']}MB allocated, {s['reserved_mb']}MB reserved")
        return "\n".join(lines)
