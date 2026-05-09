"""
OMNI Compute — LoRA (Low-Rank Adaptation) Trainer
Parameter-efficient fine-tuning for large language models.
"""
import logging, json, os, time, math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("omni.lora")

@dataclass
class LoRAConfig:
    rank: int = 16; alpha: float = 32.0; dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj","k_proj","v_proj","o_proj"])
    learning_rate: float = 2e-4; batch_size: int = 4; epochs: int = 3
    max_seq_len: int = 2048; weight_decay: float = 0.01
    warmup_steps: int = 100; output_dir: str = "./lora_output"
    use_rslora: bool = False  # Rank-stabilized LoRA

    @property
    def scaling(self) -> float:
        if self.use_rslora:
            return self.alpha / math.sqrt(self.rank)
        return self.alpha / self.rank

class LoRALayer:
    """Single LoRA adapter layer: W' = W + (B @ A) * scaling."""
    def __init__(self, in_features: int, out_features: int, rank: int, scaling: float):
        self.in_features = in_features; self.out_features = out_features
        self.rank = rank; self.scaling = scaling
        self.lora_A_shape = (rank, in_features)    # initialized with kaiming
        self.lora_B_shape = (out_features, rank)    # initialized with zeros
        self.trainable_params = rank * in_features + out_features * rank
    def param_count(self) -> int: return self.trainable_params
    def compression_ratio(self) -> float:
        original = self.in_features * self.out_features
        return original / max(self.trainable_params, 1)

class OmniLoRATrainer:
    """Production LoRA trainer for LLM fine-tuning."""
    def __init__(self, config: LoRAConfig):
        self.config = config; self.layers: Dict[str, LoRALayer] = {}
        self.metrics: List[dict] = []; self.train_data: List[dict] = []
        os.makedirs(config.output_dir, exist_ok=True)

    def inject_adapters(self, model_info: Dict[str, Tuple[int, int]]):
        """Inject LoRA adapters into target modules."""
        total_trainable = 0; total_original = 0
        for name, (in_f, out_f) in model_info.items():
            if any(t in name for t in self.config.target_modules):
                layer = LoRALayer(in_f, out_f, self.config.rank, self.config.scaling)
                self.layers[name] = layer
                total_trainable += layer.param_count()
            total_original += in_f * out_f
        pct = total_trainable / max(total_original, 1) * 100
        logger.info(f"LoRA injected: {len(self.layers)} adapters, "
                    f"{total_trainable:,} trainable params ({pct:.2f}% of {total_original:,})")

    def load_dataset(self, path: str):
        with open(path) as f:
            for line in f:
                self.train_data.append(json.loads(line.strip()))
        logger.info(f"Loaded {len(self.train_data)} training examples")

    def get_lr_schedule(self, step: int, total_steps: int) -> float:
        if step < self.config.warmup_steps:
            return self.config.learning_rate * step / max(self.config.warmup_steps, 1)
        progress = (step - self.config.warmup_steps) / max(total_steps - self.config.warmup_steps, 1)
        return self.config.learning_rate * 0.5 * (1 + math.cos(math.pi * progress))

    def log_step(self, step: int, loss: float, lr: float):
        m = {"step": step, "loss": round(loss, 6), "lr": lr, "ts": time.time()}
        self.metrics.append(m)

    def save_adapter(self, step: int):
        path = os.path.join(self.config.output_dir, f"lora-adapter-step-{step}")
        os.makedirs(path, exist_ok=True)
        meta = {"config": {k: v for k, v in vars(self.config).items() if not callable(v)},
                "layers": {n: {"in": l.in_features, "out": l.out_features, "rank": l.rank}
                           for n, l in self.layers.items()},
                "step": step, "metrics": self.metrics[-10:]}
        with open(os.path.join(path, "adapter_config.json"), "w") as f:
            json.dump(meta, f, indent=2)
        logger.info(f"LoRA adapter saved: {path}")

    def merge_and_unload(self) -> Dict:
        """Merge LoRA weights back into base model (conceptual)."""
        merged = {}
        for name, layer in self.layers.items():
            merged[name] = {"merged": True, "scaling": layer.scaling,
                           "compression": f"{layer.compression_ratio():.1f}x"}
        return merged

    def summary(self) -> Dict:
        total_params = sum(l.param_count() for l in self.layers.values())
        return {"rank": self.config.rank, "alpha": self.config.alpha,
                "num_adapters": len(self.layers), "trainable_params": total_params,
                "train_examples": len(self.train_data), "steps_logged": len(self.metrics)}
