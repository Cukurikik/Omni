"""
OMNI Transformer — Distributed Training Utilities
Data-parallel and model-parallel training support.
"""
import os
import torch
import torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def setup_distributed(backend: str = "nccl") -> int:
    """Initialize distributed training environment."""
    if "RANK" not in os.environ:
        logger.info("Running in single-GPU mode")
        return 0
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    local_rank = int(os.environ.get("LOCAL_RANK", 0))

    dist.init_process_group(backend=backend, rank=rank, world_size=world_size)
    torch.cuda.set_device(local_rank)

    logger.info(f"Distributed: rank={rank}, world={world_size}, local_rank={local_rank}")
    return local_rank


def cleanup_distributed() -> None:
    if dist.is_initialized():
        dist.destroy_process_group()


def wrap_model_ddp(model: nn.Module, local_rank: int, find_unused: bool = False) -> nn.Module:
    """Wrap model with DistributedDataParallel."""
    model = model.to(local_rank)
    return DDP(model, device_ids=[local_rank], find_unused_parameters=find_unused)


def create_distributed_dataloader(
    dataset, batch_size: int, num_workers: int = 4, collate_fn=None, seed: int = 42
) -> DataLoader:
    """Create dataloader with distributed sampler."""
    sampler = DistributedSampler(dataset, shuffle=True, seed=seed) if dist.is_initialized() else None
    return DataLoader(
        dataset, batch_size=batch_size, sampler=sampler,
        num_workers=num_workers, collate_fn=collate_fn,
        pin_memory=True, shuffle=(sampler is None),
    )


def all_reduce_mean(tensor: torch.Tensor) -> torch.Tensor:
    """Average tensor across all processes."""
    if not dist.is_initialized():
        return tensor
    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
    tensor /= dist.get_world_size()
    return tensor


def is_main_process() -> bool:
    if not dist.is_initialized():
        return True
    return dist.get_rank() == 0


class GradientSynchronizer:
    """Manage gradient synchronization for mixed precision distributed training."""
    def __init__(self, model: nn.Module, max_norm: float = 1.0):
        self.model = model
        self.max_norm = max_norm

    def sync_and_clip(self) -> float:
        if isinstance(self.model, DDP):
            # Gradients are already synced by DDP backward hook
            pass
        total_norm = nn.utils.clip_grad_norm_(self.model.parameters(), self.max_norm)
        return total_norm.item()
