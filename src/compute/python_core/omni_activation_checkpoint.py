"""OMNI Compute — Activation Checkpointing Manager"""
import logging; from dataclasses import dataclass; from typing import Dict, List
logger = logging.getLogger("omni.checkpoint")
@dataclass
class CheckpointConfig:
    strategy: str = "selective"  # none | full | selective
    checkpoint_ratio: float = 0.5  # fraction of layers to checkpoint
    offload_to_cpu: bool = False
class ActivationCheckpointer:
    """Manages gradient checkpointing for memory-efficient training."""
    def __init__(self, c: CheckpointConfig): self.config = c; self.layer_decisions: Dict[int, bool] = {}
    def decide_layers(self, num_layers: int) -> Dict[int, bool]:
        if self.config.strategy == "none": return {i: False for i in range(num_layers)}
        if self.config.strategy == "full": return {i: True for i in range(num_layers)}
        n_ckpt = max(1, int(num_layers * self.config.checkpoint_ratio))
        step = max(1, num_layers // n_ckpt)
        self.layer_decisions = {i: (i % step == 0) for i in range(num_layers)}
        return self.layer_decisions
    def memory_savings_estimate(self, num_layers: int, hidden_dim: int, seq_len: int, batch: int) -> Dict:
        activation_per_layer = batch * seq_len * hidden_dim * 4  # bytes (f32)
        total_no_ckpt = activation_per_layer * num_layers
        ckpted = sum(1 for v in self.layer_decisions.values() if v)
        total_with_ckpt = activation_per_layer * (num_layers - ckpted) + activation_per_layer * 2
        savings = 1 - total_with_ckpt / max(total_no_ckpt, 1)
        return {"no_checkpoint_mb": total_no_ckpt / (1024**2), "with_checkpoint_mb": total_with_ckpt / (1024**2),
                "savings": f"{savings*100:.1f}%", "layers_checkpointed": ckpted}
