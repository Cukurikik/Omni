"""
OMNI Compute — DPO Trainer (Direct Preference Optimization)
RLHF-free alignment training for language models.
"""
import logging, time, json, os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("omni.dpo")

@dataclass
class DPOConfig:
    beta: float = 0.1
    learning_rate: float = 1e-6; batch_size: int = 2; epochs: int = 1
    max_seq_len: int = 2048; gradient_accumulation: int = 8
    label_smoothing: float = 0.0; loss_type: str = "sigmoid"  # sigmoid | hinge | ipo
    output_dir: str = "./dpo_output"

@dataclass
class PreferencePair:
    prompt: str; chosen: str; rejected: str
    chosen_score: float = 1.0; rejected_score: float = 0.0

class OmniDPOTrainer:
    """Direct Preference Optimization trainer — no reward model needed."""
    def __init__(self, config: DPOConfig):
        self.config = config
        self.pairs: List[PreferencePair] = []
        self.metrics: List[dict] = []
        os.makedirs(config.output_dir, exist_ok=True)
    def load_preferences(self, path: str):
        """Load preference pairs from JSONL."""
        with open(path) as f:
            for line in f:
                d = json.loads(line.strip())
                self.pairs.append(PreferencePair(
                    prompt=d["prompt"], chosen=d["chosen"], rejected=d["rejected"],
                    chosen_score=d.get("chosen_score", 1.0),
                    rejected_score=d.get("rejected_score", 0.0)
                ))
        logger.info(f"Loaded {len(self.pairs)} preference pairs")
    def compute_dpo_loss(self, policy_chosen_logps: List[float], policy_rejected_logps: List[float],
                         ref_chosen_logps: List[float], ref_rejected_logps: List[float]) -> float:
        """Compute DPO loss: -log(sigmoid(beta * (log_pi(y_w) - log_pi(y_l) - log_ref(y_w) + log_ref(y_l))))"""
        import math
        total_loss = 0.0
        for pc, pr, rc, rr in zip(policy_chosen_logps, policy_rejected_logps, ref_chosen_logps, ref_rejected_logps):
            logit = self.config.beta * ((pc - rc) - (pr - rr))
            if self.config.loss_type == "sigmoid":
                loss = -math.log(1.0 / (1.0 + math.exp(-logit)) + 1e-8)
            elif self.config.loss_type == "hinge":
                loss = max(0, 1.0 - logit)
            else:  # ipo
                loss = (logit - 1.0 / (2.0 * self.config.beta)) ** 2
            total_loss += loss
        return total_loss / max(len(policy_chosen_logps), 1)
    def compute_accuracy(self, policy_chosen_logps: List[float], policy_rejected_logps: List[float],
                         ref_chosen_logps: List[float], ref_rejected_logps: List[float]) -> float:
        """Accuracy = how often the policy prefers chosen over rejected."""
        correct = 0
        for pc, pr, rc, rr in zip(policy_chosen_logps, policy_rejected_logps, ref_chosen_logps, ref_rejected_logps):
            reward_chosen = pc - rc
            reward_rejected = pr - rr
            if reward_chosen > reward_rejected: correct += 1
        return correct / max(len(policy_chosen_logps), 1)
    def log_metrics(self, step: int, loss: float, accuracy: float, lr: float):
        m = {"step": step, "loss": round(loss, 6), "accuracy": round(accuracy, 4),
             "lr": lr, "timestamp": time.time()}
        self.metrics.append(m)
        logger.info(f"Step {step}: loss={loss:.6f} acc={accuracy:.4f}")
    def save_checkpoint(self, step: int):
        path = os.path.join(self.config.output_dir, f"dpo-checkpoint-{step}")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "metrics.json"), "w") as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"DPO checkpoint saved: {path}")
    def get_summary(self) -> dict:
        return {"total_pairs": len(self.pairs), "config": vars(self.config),
                "metrics_count": len(self.metrics),
                "last_metrics": self.metrics[-1] if self.metrics else {}}
