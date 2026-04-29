# VisCPM — Cross-lingual Visual QA Pipeline
import torch
from typing import Optional, Generic, TypeVar, Dict
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class VisCPMProcessor:
    MAX_IMG_RES = 1024; MAX_TEXT_LEN = 4096
    def process_image_question(self, image: torch.Tensor, question: str, lang: str = "zh") -> OmniResult[Dict, str]:
        if image.dim() != 3: return OmniResult(error="Expected [C,H,W] image tensor")
        if image.shape[1] > self.MAX_IMG_RES or image.shape[2] > self.MAX_IMG_RES:
            return OmniResult(error=f"Image exceeds {self.MAX_IMG_RES}px")
        if len(question) > self.MAX_TEXT_LEN: return OmniResult(error="Question exceeds 4KB")
        if lang not in ["zh", "en"]: return OmniResult(error="Language must be zh or en")
        return OmniResult(value={"question": question, "lang": lang, "status": "processed"})
