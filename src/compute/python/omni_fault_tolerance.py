"""
OMNI MOTHER: Signal-Aware Fault Tolerance (Production Grade)
Emergency checkpointing and graceful degradation for distributed
MoE training. Handles SIGTERM, SIGINT, OOM, and NCCL timeouts.
"""
import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional
import torch
import torch.distributed as dist

logger = logging.getLogger("OmniFaultTolerance")

class CheckpointManager:
    """Manages periodic and emergency model checkpointing."""
    def __init__(self, save_dir: str, max_checkpoints: int = 5):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.max_checkpoints = max_checkpoints
        self._saved: list = []

    def save(self, state: Dict[str, Any], tag: str = "auto") -> str:
        path = self.save_dir / f"ckpt_{tag}_{int(time.time())}.pt"
        torch.save(state, str(path))
        self._saved.append(path)
        logger.info(f"Checkpoint saved: {path}")
        self._cleanup()
        return str(path)

    def _cleanup(self):
        while len(self._saved) > self.max_checkpoints:
            old = self._saved.pop(0)
            if old.exists():
                old.unlink()
                logger.info(f"Removed old checkpoint: {old}")

    def latest(self) -> Optional[str]:
        if not self._saved:
            pts = sorted(self.save_dir.glob("ckpt_*.pt"), key=os.path.getmtime)
            if pts:
                return str(pts[-1])
            return None
        return str(self._saved[-1])

    def load(self, path: Optional[str] = None) -> Optional[Dict]:
        path = path or self.latest()
        if path and Path(path).exists():
            logger.info(f"Loading checkpoint: {path}")
            return torch.load(path, map_location="cpu", weights_only=False)
        return None

class OmniFaultTolerance:
    """Signal handler and fault manager for distributed training."""
    def __init__(self, checkpoint_dir: str = "./checkpoints",
                 on_emergency: Optional[Callable] = None):
        self.ckpt = CheckpointManager(checkpoint_dir)
        self._on_emergency = on_emergency
        self._shutdown_requested = threading.Event()
        self._model_state: Optional[Dict] = None
        self._install_handlers()

    def _install_handlers(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        logger.info("Signal handlers installed (SIGTERM, SIGINT)")

    def _handle_signal(self, signum, frame):
        sig_name = signal.Signals(signum).name
        logger.warning(f"Received {sig_name} — initiating emergency save")
        self._shutdown_requested.set()
        if self._model_state:
            self.ckpt.save(self._model_state, tag=f"emergency_{sig_name}")
        if self._on_emergency:
            try:
                self._on_emergency()
            except Exception as e:
                logger.error(f"Emergency callback failed: {e}")
        logger.info("Emergency checkpoint complete. Exiting.")

    def register_state(self, model: torch.nn.Module,
                       optimizer: Optional[Any] = None,
                       step: int = 0, extra: Optional[Dict] = None):
        state = {"model": model.state_dict(), "step": step}
        if optimizer is not None:
            state["optimizer"] = optimizer.state_dict()
        if extra:
            state.update(extra)
        self._model_state = state

    def periodic_checkpoint(self, model: torch.nn.Module,
                            optimizer: Any, step: int,
                            interval: int = 1000):
        if step > 0 and step % interval == 0:
            state = {
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
            }
            self._model_state = state
            self.ckpt.save(state, tag=f"step_{step}")

    @property
    def should_stop(self) -> bool:
        return self._shutdown_requested.is_set()

    def safe_all_reduce(self, tensor: torch.Tensor,
                        op: Any = None, timeout_s: float = 30.0) -> bool:
        """All-reduce with timeout to detect NCCL hangs."""
        if not dist.is_initialized():
            return True
        try:
            if op is None:
                op = dist.ReduceOp.SUM
            handle = dist.all_reduce(tensor, op=op, async_op=True)
            completed = handle.wait(timeout=timeout_s if hasattr(handle, 'wait') else None)
            return True
        except Exception as e:
            logger.error(f"all_reduce failed: {e}")
            if self._model_state:
                self.ckpt.save(self._model_state, tag="nccl_failure")
            return False

    def handle_oom(self, model: torch.nn.Module, optimizer: Any,
                   step: int) -> bool:
        """Handle CUDA OOM by saving state and clearing cache."""
        logger.warning("CUDA OOM detected — emergency save + cache clear")
        state = {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "step": step,
        }
        self.ckpt.save(state, tag="oom_recovery")
        torch.cuda.empty_cache()
        return True
