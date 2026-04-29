from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI TOCFL MultiBench Engine — Compute Layer
# Absorbing Shengwei-Peng/TOCFL-MultiBench: Multimodal Chinese proficiency benchmark with STCM.

@dataclass
class BenchResult:
    ok: bool
    score: float = 0.0
    level: str = ""
    error: str = None

class OmniTocflMultibenchEngine:
    LEVELS = ["Novice", "Band-A", "Band-B", "Band-C", "Band-D"]

    def __init__(self):
        self.evaluations = 0

    def evaluate_proficiency(self, text_logits: np.ndarray, audio_logits: np.ndarray,
                             image_logits: np.ndarray, ground_truth: int) -> BenchResult:
        if any(x.ndim != 1 for x in [text_logits, audio_logits, image_logits]):
            return BenchResult(False, error="TOCFLError: All logit arrays must be 1D")
        if not all(x.shape == text_logits.shape for x in [audio_logits, image_logits]):
            return BenchResult(False, error="TOCFLError: Shape mismatch across modalities")
        try:
            self.evaluations += 1
            # STCM: Selective Token Constraint — weight modalities by confidence (max logit value)
            text_conf = float(np.max(text_logits) - np.mean(text_logits))
            audio_conf = float(np.max(audio_logits) - np.mean(audio_logits))
            image_conf = float(np.max(image_logits) - np.mean(image_logits))
            total_conf = text_conf + audio_conf + image_conf + 1e-10

            w_t = text_conf / total_conf
            w_a = audio_conf / total_conf
            w_i = image_conf / total_conf

            fused = w_t * text_logits + w_a * audio_logits + w_i * image_logits
            predicted = int(np.argmax(fused))
            correct = 1.0 if predicted == ground_truth else 0.0
            level_idx = min(predicted, len(self.LEVELS) - 1)
            return BenchResult(True, score=correct, level=self.LEVELS[level_idx])
        except Exception as e:
            return BenchResult(False, error=f"TOCFLError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniTocflMultibenchEngine", "evaluations": self.evaluations, "status": "Operational"}
