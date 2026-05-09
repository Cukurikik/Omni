"""
omni_wandb_logger.py — Experiment Logger Abstraction
Inspired by: W&B/MLflow/TensorBoard logging for OMNI training
Layer: Compute / AI

Unified logging interface with file-based persistence,
metric aggregation, and checkpoint management.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    step: int
    timestamp: float
    metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunConfig:
    project: str
    run_name: str
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


class MetricAggregator:
    """Aggregates metrics over a window for smoothed logging."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.buffers: Dict[str, List[float]] = {}

    def add(self, name: str, value: float):
        if name not in self.buffers:
            self.buffers[name] = []
        self.buffers[name].append(value)
        if len(self.buffers[name]) > self.window_size:
            self.buffers[name] = self.buffers[name][-self.window_size:]

    def get_mean(self, name: str) -> Optional[float]:
        if name not in self.buffers or not self.buffers[name]:
            return None
        return sum(self.buffers[name]) / len(self.buffers[name])

    def get_latest(self, name: str) -> Optional[float]:
        if name not in self.buffers or not self.buffers[name]:
            return None
        return self.buffers[name][-1]

    def get_min(self, name: str) -> Optional[float]:
        if name not in self.buffers or not self.buffers[name]:
            return None
        return min(self.buffers[name])

    def get_max(self, name: str) -> Optional[float]:
        if name not in self.buffers or not self.buffers[name]:
            return None
        return max(self.buffers[name])

    def get_all_means(self) -> Dict[str, float]:
        result = {}
        for name in self.buffers:
            mean = self.get_mean(name)
            if mean is not None:
                result[name] = mean
        return result


class CheckpointManager:
    """Manage model checkpoint files with retention policy."""

    def __init__(self, save_dir: str, max_checkpoints: int = 5,
                 metric_name: str = "val_loss", mode: str = "min"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.max_checkpoints = max_checkpoints
        self.metric_name = metric_name
        self.mode = mode
        self.checkpoints: List[Dict[str, Any]] = []

    def should_save(self, metrics: Dict[str, float]) -> bool:
        """Determine if current metrics warrant saving."""
        if self.metric_name not in metrics:
            return True

        current = metrics[self.metric_name]
        if not self.checkpoints:
            return True

        best = self._get_best_metric()
        if self.mode == "min":
            return current < best
        return current > best

    def register_checkpoint(self, path: str, step: int,
                            metrics: Dict[str, float]):
        """Register a saved checkpoint."""
        entry = {
            "path": path,
            "step": step,
            "metrics": metrics,
            "timestamp": time.time(),
        }
        self.checkpoints.append(entry)
        self._cleanup()

    def _get_best_metric(self) -> float:
        values = [c["metrics"].get(self.metric_name, float("inf"))
                  for c in self.checkpoints]
        if self.mode == "min":
            return min(values) if values else float("inf")
        return max(values) if values else float("-inf")

    def _cleanup(self):
        """Remove old checkpoints beyond retention limit."""
        if len(self.checkpoints) <= self.max_checkpoints:
            return

        # Sort by metric value (keep best)
        key_fn = lambda c: c["metrics"].get(self.metric_name, float("inf"))
        reverse = self.mode == "max"
        sorted_ckpts = sorted(self.checkpoints, key=key_fn, reverse=reverse)

        to_remove = sorted_ckpts[self.max_checkpoints:]
        self.checkpoints = sorted_ckpts[:self.max_checkpoints]

        for ckpt in to_remove:
            path = Path(ckpt["path"])
            if path.exists():
                try:
                    path.unlink()
                    logger.info(f"Removed checkpoint: {path}")
                except OSError:
                    pass

    @property
    def best_checkpoint(self) -> Optional[Dict[str, Any]]:
        if not self.checkpoints:
            return None
        key_fn = lambda c: c["metrics"].get(self.metric_name, float("inf"))
        if self.mode == "min":
            return min(self.checkpoints, key=key_fn)
        return max(self.checkpoints, key=key_fn)


class OmniLogger:
    """Unified experiment logging with file persistence.

    Features:
    - JSONL-based metric logging for easy parsing
    - Metric aggregation with windowed smoothing
    - Checkpoint management with retention policy
    - Configuration and hyperparameter tracking
    - Compatible with external loggers (W&B, MLflow)
    """

    def __init__(self, run_config: RunConfig, log_dir: str = "./omni_logs"):
        self.config = run_config
        self.log_dir = Path(log_dir) / run_config.project / run_config.run_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.aggregator = MetricAggregator()
        self.checkpoint_manager = CheckpointManager(
            str(self.log_dir / "checkpoints")
        )

        self._log_file = open(self.log_dir / "metrics.jsonl", "a")
        self._step = 0
        self._start_time = time.time()
        self._entries: List[LogEntry] = []

        # Save run config
        config_path = self.log_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(asdict(run_config), f, indent=2, default=str)

        logger.info(f"OmniLogger initialized: {self.log_dir}")

    def log(self, metrics: Dict[str, float], step: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None):
        """Log metrics for a training step."""
        if step is not None:
            self._step = step
        else:
            self._step += 1

        # Update aggregator
        for name, value in metrics.items():
            self.aggregator.add(name, value)

        # Create log entry
        entry = LogEntry(
            step=self._step,
            timestamp=time.time() - self._start_time,
            metrics=metrics,
            metadata=metadata or {},
        )
        self._entries.append(entry)

        # Write to JSONL file
        line = json.dumps(asdict(entry), default=str)
        self._log_file.write(line + "\n")
        self._log_file.flush()

    def log_summary(self, prefix: str = ""):
        """Log aggregated metric summary."""
        summary = {}
        for name in self.aggregator.buffers:
            key = f"{prefix}{name}" if prefix else name
            summary[f"{key}_mean"] = self.aggregator.get_mean(name) or 0
            summary[f"{key}_min"] = self.aggregator.get_min(name) or 0
            summary[f"{key}_max"] = self.aggregator.get_max(name) or 0
        self.log(summary, step=self._step)

    def log_hyperparams(self, params: Dict[str, Any]):
        """Log hyperparameters."""
        hp_path = self.log_dir / "hyperparams.json"
        with open(hp_path, "w") as f:
            json.dump(params, f, indent=2, default=str)

    def save_checkpoint(self, state_dict: Dict, metrics: Dict[str, float]):
        """Save a model checkpoint if metrics improve."""
        import torch

        if self.checkpoint_manager.should_save(metrics):
            path = str(self.log_dir / "checkpoints" / f"step_{self._step}.pt")
            torch.save(state_dict, path)
            self.checkpoint_manager.register_checkpoint(path, self._step, metrics)
            logger.info(f"Saved checkpoint at step {self._step}")

    def get_best_metric(self, name: str) -> Optional[float]:
        return self.aggregator.get_min(name)

    def get_history(self, metric_name: str) -> List[Dict[str, Any]]:
        """Get full history for a specific metric."""
        return [
            {"step": e.step, "value": e.metrics.get(metric_name),
             "timestamp": e.timestamp}
            for e in self._entries
            if metric_name in e.metrics
        ]

    def finish(self):
        """Finalize logging session."""
        summary = {
            "total_steps": self._step,
            "total_time_s": time.time() - self._start_time,
            "final_metrics": self.aggregator.get_all_means(),
            "best_checkpoint": self.checkpoint_manager.best_checkpoint,
        }

        summary_path = self.log_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        self._log_file.close()
        logger.info(f"Logging complete: {self._step} steps, {self.log_dir}")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.finish()
