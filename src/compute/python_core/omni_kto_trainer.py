"""
OMNI Compute — KTO Trainer (Kahneman-Tversky Optimization)
Binary preference alignment without paired comparisons.
"""
import logging, json, os, time, math
from dataclasses import dataclass, field
from typing import List, Dict

logger = logging.getLogger("omni.kto")

@dataclass
class KTOConfig:
    beta: float = 0.1; desirable_weight: float = 1.0; undesirable_weight: float = 1.0
    learning_rate: float = 5e-7; batch_size: int = 4; epochs: int = 1
    output_dir: str = "./kto_output"

@dataclass
class KTOSample:
    prompt: str; response: str; is_desirable: bool
    log_prob: float = 0.0; ref_log_prob: float = 0.0

class OmniKTOTrainer:
    """KTO: alignment from binary signals (thumbs up/down) without pairs."""
    def __init__(self, config: KTOConfig):
        self.config = config; self.data: List[KTOSample] = []; self.metrics: List[dict] = []
        os.makedirs(config.output_dir, exist_ok=True)
    def load_data(self, path: str):
        with open(path) as f:
            for line in f:
                d = json.loads(line.strip())
                self.data.append(KTOSample(prompt=d["prompt"], response=d["response"],
                                           is_desirable=d.get("is_desirable", d.get("label", True))))
        logger.info(f"Loaded {len(self.data)} samples ({sum(1 for s in self.data if s.is_desirable)} desirable)")
    def compute_kto_loss(self, samples: List[KTOSample]) -> float:
        """KTO loss: asymmetric treatment of desirable vs undesirable."""
        kl_desirable = sum(s.ref_log_prob - s.log_prob for s in samples if s.is_desirable)
        n_des = max(sum(1 for s in samples if s.is_desirable), 1)
        kl_d = kl_desirable / n_des
        total_loss = 0.0
        for s in samples:
            log_ratio = s.log_prob - s.ref_log_prob
            if s.is_desirable:
                loss = -self.config.desirable_weight * math.log(1/(1+math.exp(-self.config.beta*(log_ratio-kl_d)))+1e-8)
            else:
                loss = -self.config.undesirable_weight * math.log(1/(1+math.exp(self.config.beta*(log_ratio-kl_d)))+1e-8)
            total_loss += loss
        return total_loss / max(len(samples), 1)
    def log_step(self, step: int, loss: float):
        m = {"step": step, "loss": round(loss, 6), "ts": time.time()}
        self.metrics.append(m)
    def save(self, step: int):
        p = os.path.join(self.config.output_dir, f"kto-{step}")
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, "metrics.json"), "w") as f: json.dump(self.metrics, f, indent=2)
    def summary(self) -> dict:
        des = sum(1 for s in self.data if s.is_desirable)
        return {"total": len(self.data), "desirable": des, "undesirable": len(self.data)-des,
                "steps": len(self.metrics)}
