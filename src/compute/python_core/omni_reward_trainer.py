"""OMNI Compute — RLHF Reward Model Trainer"""
import logging, json, os, time, math; from dataclasses import dataclass, field; from typing import List, Dict, Tuple
logger = logging.getLogger("omni.reward")

@dataclass
class RewardConfig:
    learning_rate: float = 1e-5; batch_size: int = 8; epochs: int = 1
    max_seq_len: int = 2048; margin: float = 0.0; output_dir: str = "./reward_output"

@dataclass
class ComparisonPair:
    prompt: str; chosen: str; rejected: str
    chosen_score: float = 0.0; rejected_score: float = 0.0

class OmniRewardTrainer:
    """Reward model trainer for RLHF preference learning."""
    def __init__(self, config: RewardConfig):
        self.config = config; self.data: List[ComparisonPair] = []; self.metrics: List[dict] = []
        os.makedirs(config.output_dir, exist_ok=True)
    def load_comparisons(self, path: str):
        with open(path) as f:
            for line in f:
                d = json.loads(line.strip())
                self.data.append(ComparisonPair(prompt=d["prompt"], chosen=d["chosen"], rejected=d["rejected"]))
        logger.info(f"Loaded {len(self.data)} comparison pairs")
    def compute_loss(self, chosen_scores: List[float], rejected_scores: List[float]) -> float:
        """Bradley-Terry loss: -log(sigmoid(score_chosen - score_rejected))"""
        total = 0.0
        for c, r in zip(chosen_scores, rejected_scores):
            diff = c - r - self.config.margin
            total += -math.log(1 / (1 + math.exp(-diff)) + 1e-8)
        return total / max(len(chosen_scores), 1)
    def compute_accuracy(self, chosen_scores: List[float], rejected_scores: List[float]) -> float:
        correct = sum(1 for c, r in zip(chosen_scores, rejected_scores) if c > r)
        return correct / max(len(chosen_scores), 1)
    def log_step(self, step: int, loss: float, acc: float):
        self.metrics.append({"step": step, "loss": round(loss, 6), "accuracy": round(acc, 4), "ts": time.time()})
    def save(self, step: int):
        p = os.path.join(self.config.output_dir, f"reward-{step}")
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, "metrics.json"), "w") as f: json.dump(self.metrics, f, indent=2)
    def summary(self) -> Dict:
        return {"pairs": len(self.data), "steps": len(self.metrics),
                "last": self.metrics[-1] if self.metrics else {}}
