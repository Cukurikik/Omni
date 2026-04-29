# VisionLLM — Detection Head with Box Regression
import torch
from typing import Optional, Generic, TypeVar, List, Dict
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class VisionLLMDetector:
    MAX_BOXES = 5000; MAX_CLASSES = 10000
    def __init__(self, num_classes: int):
        if num_classes > self.MAX_CLASSES: raise ValueError(f"Classes exceed {self.MAX_CLASSES}")
        self.num_classes = num_classes

    def decode_predictions(self, logits: torch.Tensor, boxes: torch.Tensor, score_threshold: float = 0.3) -> OmniResult[List[Dict], str]:
        if logits.dim() != 2: return OmniResult(error="Expected [N, C] logits")
        if boxes.dim() != 2 or boxes.shape[1] != 4: return OmniResult(error="Expected [N, 4] boxes")
        if logits.shape[0] != boxes.shape[0]: return OmniResult(error="Logits/boxes count mismatch")
        if logits.shape[0] > self.MAX_BOXES: return OmniResult(error=f"Boxes exceed {self.MAX_BOXES}")
        probs = torch.softmax(logits, dim=-1)
        max_probs, class_ids = probs.max(dim=-1)
        mask = max_probs > score_threshold
        results = []
        for i in mask.nonzero(as_tuple=True)[0]:
            idx = i.item()
            results.append({"class_id": class_ids[idx].item(), "score": max_probs[idx].item(),
                            "box": boxes[idx].tolist()})
        return OmniResult(value=results)
