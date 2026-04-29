# Omni Efficient-AIGC Compression Benchmark (Python)
# Ref: Efficient-ML/Awesome-Efficient-AIGC
from typing import List, Dict
import math

def compute_compression_ratio(original_size: int, compressed_size: int) -> float:
    return round(original_size / max(compressed_size, 1), 2)

def sparsity_analysis(weights: List[float], threshold: float = 1e-6) -> Dict:
    zeros = sum(1 for w in weights if abs(w) < threshold)
    return {"total": len(weights), "zeros": zeros,
            "sparsity": round(zeros / max(len(weights), 1), 4)}

def distillation_gap(teacher_logits: List[float], student_logits: List[float]) -> float:
    n = min(len(teacher_logits), len(student_logits))
    return round(math.sqrt(sum((t - s)**2 for t, s in zip(teacher_logits[:n], student_logits[:n])) / max(n, 1)), 6)
