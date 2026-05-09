"""
@omni-layer Compute | @omni-source PaddlePaddle/PALM
@omni-description Multi-task NLP pretraining framework: parallel task training with
shared backbone, task-specific heads, and gradient accumulation.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniPALMMultiTaskTrainer:
    """Multi-task pretraining with shared backbone and task-specific heads."""
    def __init__(self, d_model: int = 768, task_configs: Optional[Dict] = None):
        self.d_model = d_model
        self.task_configs = task_configs or {"mlm": {"weight": 1.0, "n_classes": 30522}, "nsp": {"weight": 0.5, "n_classes": 2}, "ner": {"weight": 0.8, "n_classes": 9}, "sentiment": {"weight": 0.6, "n_classes": 3}}
        self.task_heads = {}
        for task, cfg in self.task_configs.items():
            self.task_heads[task] = [[math.sin((i+1)*(j+1)*0.002) * 0.01 for j in range(d_model)] for i in range(cfg["n_classes"])]

    def forward_task(self, hidden_states: List[List[float]], task_name: str) -> OmniResult:
        try:
            if task_name not in self.task_heads:
                return OmniResult(error=Exception(f"Unknown task: {task_name}"))
            head = self.task_heads[task_name]
            n_cls = len(head)
            logits = []
            for h in hidden_states:
                token_logits = [sum(head[c][j] * h[j] for j in range(min(len(h), self.d_model))) for c in range(n_cls)]
                logits.append(token_logits)
            return OmniResult(data={"task": task_name, "logits_shape": [len(logits), n_cls], "n_classes": n_cls})
        except Exception as e:
            return OmniResult(error=Exception(f"Task forward failed: {e}"))

    def multi_task_loss(self, task_losses: Dict[str, float]) -> OmniResult:
        try:
            weighted_loss = 0.0
            for task, loss in task_losses.items():
                weight = self.task_configs.get(task, {}).get("weight", 1.0)
                weighted_loss += weight * loss
            return OmniResult(data={"total_loss": weighted_loss, "task_losses": task_losses, "n_tasks": len(task_losses)})
        except Exception as e:
            return OmniResult(error=Exception(f"Multi-task loss failed: {e}"))

    def gradient_accumulation_step(self, gradients_batch: List[List[float]], accumulation_steps: int = 4) -> OmniResult:
        try:
            if not gradients_batch:
                return OmniResult(error=Exception("No gradients"))
            d = len(gradients_batch[0])
            accumulated = [sum(gradients_batch[b][j] for b in range(len(gradients_batch))) / accumulation_steps for j in range(d)]
            grad_norm = math.sqrt(sum(g**2 for g in accumulated))
            return OmniResult(data={"accumulated_grad_norm": grad_norm, "n_batches": len(gradients_batch), "accum_steps": accumulation_steps})
        except Exception as e:
            return OmniResult(error=Exception(f"Grad accum failed: {e}"))
