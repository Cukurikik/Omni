"""
OMNI Compute — SFT Trainer for Reasoning Models (tiny-reasoning-LM-inspired)
Supervised fine-tuning pipeline for small reasoning language models.
"""
import logging, time, json, os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from pathlib import Path

logger = logging.getLogger("omni.sft_trainer")

@dataclass
class SFTConfig:
    model_name: str = "omni-350m"
    learning_rate: float = 2e-5; batch_size: int = 4; epochs: int = 3
    max_seq_len: int = 2048; warmup_ratio: float = 0.1
    weight_decay: float = 0.01; gradient_accumulation: int = 4
    save_steps: int = 500; eval_steps: int = 100
    output_dir: str = "./sft_output"; fp16: bool = True
    gradient_checkpointing: bool = True

@dataclass
class TrainingExample:
    instruction: str; input_text: str = ""; output_text: str = ""
    system_prompt: str = "You are a helpful reasoning assistant."
    def to_chat_format(self) -> str:
        parts = [f"<|system|>{self.system_prompt}</s>"]
        prompt = self.instruction
        if self.input_text: prompt += f"\n\nInput: {self.input_text}"
        parts.append(f"<|user|>{prompt}</s>")
        parts.append(f"<|assistant|>{self.output_text}</s>")
        return "\n".join(parts)

class OmniSFTTrainer:
    """Production SFT trainer for reasoning language models."""
    def __init__(self, config: SFTConfig):
        self.config = config
        self.train_data: List[TrainingExample] = []
        self.eval_data: List[TrainingExample] = []
        self.metrics_history: List[dict] = []
        os.makedirs(config.output_dir, exist_ok=True)
    def load_dataset(self, path: str, split: str = "train"):
        """Load JSONL dataset."""
        examples = []
        with open(path) as f:
            for line in f:
                data = json.loads(line.strip())
                examples.append(TrainingExample(
                    instruction=data.get("instruction", ""),
                    input_text=data.get("input", ""),
                    output_text=data.get("output", ""),
                    system_prompt=data.get("system", "You are a helpful reasoning assistant.")
                ))
        if split == "train": self.train_data = examples
        else: self.eval_data = examples
        logger.info(f"Loaded {len(examples)} examples for {split}")
    def prepare_tokenized_dataset(self, tokenizer_fn: Callable[[str], Dict]):
        """Tokenize all examples."""
        tokenized = []
        for ex in self.train_data:
            text = ex.to_chat_format()
            tokens = tokenizer_fn(text)
            if len(tokens.get("input_ids", [])) <= self.config.max_seq_len:
                tokenized.append(tokens)
        logger.info(f"Tokenized {len(tokenized)}/{len(self.train_data)} examples")
        return tokenized
    def compute_metrics(self, predictions, references) -> dict:
        """Compute evaluation metrics."""
        correct = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
        return {"accuracy": correct / max(len(predictions), 1),
                "total": len(predictions), "correct": correct}
    def save_checkpoint(self, step: int, model_state: dict):
        path = Path(self.config.output_dir) / f"checkpoint-{step}"
        path.mkdir(exist_ok=True)
        # In production: torch.save(model_state, path / "model.pt")
        config_path = path / "training_config.json"
        with open(config_path, "w") as f:
            json.dump({"step": step, "config": vars(self.config),
                       "metrics": self.metrics_history[-1] if self.metrics_history else {}}, f, indent=2)
        logger.info(f"Checkpoint saved: {path}")
    def log_metrics(self, step: int, metrics: dict):
        metrics["step"] = step; metrics["timestamp"] = time.time()
        self.metrics_history.append(metrics)
        logger.info(f"Step {step}: {metrics}")
    def get_training_summary(self) -> dict:
        return {"model": self.config.model_name, "train_examples": len(self.train_data),
                "eval_examples": len(self.eval_data), "epochs": self.config.epochs,
                "total_steps": len(self.train_data) * self.config.epochs // (self.config.batch_size * self.config.gradient_accumulation),
                "metrics_history": self.metrics_history}
