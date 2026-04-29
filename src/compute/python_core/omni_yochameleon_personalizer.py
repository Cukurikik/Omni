# Omni YoChameleon Personalizer (Python)
# Compute Layer: Personalized multimodal generation with soft prompts.
# Ref: WisconsinAIVision/YoChameleon — CVPR 2025, Personalized Chameleon.

from typing import List, Dict
import math

class PersonalToken:
    __slots__ = ('token_id', 'embedding', 'subject')
    def __init__(self, token_id: int, embedding: List[float], subject: str):
        self.token_id = token_id
        self.embedding = embedding
        self.subject = subject

def compute_personalization_loss(pred: List[float], target: List[float]) -> float:
    if len(pred) != len(target) or not pred: return float('inf')
    return round(sum((p - t)**2 for p, t in zip(pred, target)) / len(pred), 10)

def merge_soft_prompts(base: List[float], personal: List[float], alpha: float = 0.3) -> List[float]:
    if len(base) != len(personal): return base
    return [round(alpha * p + (1 - alpha) * b, 8) for b, p in zip(base, personal)]
