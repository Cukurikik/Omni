"""
OMNI Compute — GRPO Trainer (Group Relative Policy Optimization)
DeepSeek-R1 inspired group-relative reinforcement learning for reasoning.
"""
import logging, math, json, os, time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

logger = logging.getLogger("omni.grpo")

@dataclass
class GRPOConfig:
    group_size: int = 8          # Number of samples per prompt
    kl_coeff: float = 0.05       # KL penalty coefficient
    clip_range: float = 0.2      # PPO-style clipping
    learning_rate: float = 5e-7
    batch_size: int = 1; epochs: int = 1
    max_seq_len: int = 4096
    reward_baseline: str = "group_mean"  # group_mean | group_median
    output_dir: str = "./grpo_output"

@dataclass
class GRPOSample:
    prompt: str; response: str; reward: float
    log_prob: float = 0.0; ref_log_prob: float = 0.0; advantage: float = 0.0

class OmniGRPOTrainer:
    """Group Relative Policy Optimization — no critic model needed."""
    def __init__(self, config: GRPOConfig):
        self.config = config; self.metrics: List[dict] = []
        os.makedirs(config.output_dir, exist_ok=True)
    def compute_group_advantages(self, groups: List[List[GRPOSample]]) -> List[List[GRPOSample]]:
        """Compute advantages relative to group baseline."""
        for group in groups:
            rewards = [s.reward for s in group]
            if self.config.reward_baseline == "group_mean":
                baseline = sum(rewards) / len(rewards)
                std = math.sqrt(sum((r - baseline)**2 for r in rewards) / len(rewards)) or 1.0
            else:
                sorted_r = sorted(rewards)
                baseline = sorted_r[len(sorted_r)//2]
                std = max(max(rewards) - min(rewards), 1e-8)
            for s in group:
                s.advantage = (s.reward - baseline) / std
        return groups
    def compute_grpo_loss(self, samples: List[GRPOSample]) -> Tuple[float, Dict]:
        """GRPO loss: clipped surrogate with KL penalty."""
        total_loss, total_kl, total_reward = 0.0, 0.0, 0.0
        for s in samples:
            ratio = math.exp(s.log_prob - s.ref_log_prob)
            clipped_ratio = max(1 - self.config.clip_range, min(1 + self.config.clip_range, ratio))
            surr1 = ratio * s.advantage
            surr2 = clipped_ratio * s.advantage
            policy_loss = -min(surr1, surr2)
            kl = s.ref_log_prob - s.log_prob
            total_loss += policy_loss + self.config.kl_coeff * kl
            total_kl += kl; total_reward += s.reward
        n = max(len(samples), 1)
        return total_loss / n, {"avg_kl": total_kl/n, "avg_reward": total_reward/n, "avg_loss": total_loss/n}
    def group_samples(self, samples: List[GRPOSample]) -> List[List[GRPOSample]]:
        """Group samples by prompt."""
        groups: Dict[str, List[GRPOSample]] = {}
        for s in samples:
            groups.setdefault(s.prompt, []).append(s)
        return list(groups.values())
    def log_metrics(self, step: int, metrics: Dict):
        m = {"step": step, **metrics, "timestamp": time.time()}
        self.metrics.append(m); logger.info(f"GRPO Step {step}: {metrics}")
    def save_checkpoint(self, step: int):
        path = os.path.join(self.config.output_dir, f"grpo-step-{step}")
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "metrics.json"), "w") as f:
            json.dump(self.metrics, f, indent=2)
    def get_summary(self) -> Dict:
        return {"config": vars(self.config), "steps": len(self.metrics),
                "last": self.metrics[-1] if self.metrics else {}}
