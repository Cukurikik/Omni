from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI OOD CLIP Detector Engine — Compute Layer
# Absorbing Andy-wyx/cloud (CSCI2470 OOD Object detection with CLIP)
# Computes Out-of-Distribution thresholds using CLIP energy scoring.

@dataclass
class OodResult:
    ok: bool
    is_ood: bool = False
    energy_score: float = 0.0
    error: str = None

class OmniOodClipDetector:
    def __init__(self, temperature: float = 1.0, ood_threshold: float = -5.0):
        self.temperature = temperature
        self.ood_threshold = ood_threshold
        self.scans = 0

    def detect_ood(self, clip_logits: np.ndarray) -> OodResult:
        """
        clip_logits: (num_classes,) array of raw dot products from CLIP.
        Calculates energy score: -T * log(sum(exp(logits / T))).
        """
        if clip_logits.ndim != 1:
            return OodResult(False, error="OodError: Expected 1D logits array")
            
        try:
            self.scans += 1
            
            # Energy formulation for OOD detection
            # High energy (less negative) = In-Distribution
            # Low energy (more negative) = Out-of-Distribution
            
            # Numerically stable LogSumExp
            max_logit = np.max(clip_logits / self.temperature)
            sum_exp = np.sum(np.exp((clip_logits / self.temperature) - max_logit))
            log_sum_exp = max_logit + np.log(sum_exp)
            
            energy = -self.temperature * log_sum_exp
            
            # Thresholding
            is_ood = bool(energy < self.ood_threshold)
            
            return OodResult(True, is_ood=is_ood, energy_score=float(energy))
        except Exception as e:
            return OodResult(False, error=f"OodError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniOodClipDetector", "scans": self.scans, "status": "Operational"}
