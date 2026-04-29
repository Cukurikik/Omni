# Omni HCGF LLM Fine-Tuning Engine
# Ref: hscspring/hcgf — Apache-2.0
# Implements: LoRA fine-tuning with gradient checkpointing for ChatGLM/LLaMA
import math
from typing import List, Dict

def lora_forward(x: List[float], weight_a: List[List[float]], weight_b: List[List[float]],
                 alpha: float = 16, rank: int = 8) -> List[float]:
    hidden = [sum(x[j] * weight_a[j][i] for j in range(min(len(x), len(weight_a))))
              for i in range(rank)]
    output = [sum(hidden[j] * weight_b[j][i] for j in range(rank))
              for i in range(len(weight_b[0]) if weight_b else 0)]
    scale = alpha / rank
    return [round(o * scale, 8) for o in output]

def compute_chat_loss(logits: List[float], targets: List[int]) -> float:
    loss = 0
    for i, (l, t) in enumerate(zip(logits, targets)):
        loss += max(-l * (1 if t else -1), 0)
    return round(loss / max(len(targets), 1), 6)

def gradient_checkpoint_partition(n_layers: int, n_checkpoints: int) -> List[List[int]]:
    chunk_size = max(1, n_layers // n_checkpoints)
    return [list(range(i, min(i + chunk_size, n_layers))) for i in range(0, n_layers, chunk_size)]
