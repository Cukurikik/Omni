from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI ME-FAS Face Anti-Spoofing Engine — Compute Layer
# Absorbing clpbc/ME-FAS: Multimodal Text Enhancement for Cross-Domain Face Anti-Spoofing.
# Generates liveliness scores using image and spoof-text descriptors.

@dataclass
class FasResult:
    ok: bool
    liveliness_score: float = 0.0
    classification: str = ""
    error: str = None

class OmniMeFasEngine:
    def __init__(self, embed_dim: int = 512):
        self.embed_dim = embed_dim
        self.verifications = 0
        np.random.seed(111)
        # Learnable margin parameter for contrastive alignment
        self.margin = 0.2

    def verify_liveliness(self, image_features: np.ndarray, text_descriptors: np.ndarray) -> FasResult:
        """
        Compares facial image features against live vs spoof textual descriptor clusters.
        image_features: (embed_dim,)
        text_descriptors: (2, embed_dim) row 0: live descriptor, row 1: spoof descriptor
        """
        if image_features.shape != (self.embed_dim,):
            return FasResult(False, error="FasError: Invalid image features")
        if text_descriptors.shape != (2, self.embed_dim):
            return FasResult(False, error="FasError: Invalid text descriptors")

        try:
            self.verifications += 1
            i_norm = image_features / max(np.linalg.norm(image_features), 1e-8)
            live_feat = text_descriptors[0] / max(np.linalg.norm(text_descriptors[0]), 1e-8)
            spoof_feat = text_descriptors[1] / max(np.linalg.norm(text_descriptors[1]), 1e-8)

            sim_live = float(np.dot(i_norm, live_feat))
            sim_spoof = float(np.dot(i_norm, spoof_feat))

            # Apply ME-FAS enhancement margin
            margin_diff = sim_live - sim_spoof + self.margin
            
            # Sigmoid bounded score 0 (spoof) to 1 (live)
            liveliness_score = 1.0 / (1.0 + np.exp(-margin_diff * 10)) # Steepness factor
            
            classification = "LIVE" if liveliness_score > 0.5 else "SPOOF"
            
            return FasResult(True, liveliness_score=liveliness_score, classification=classification)
        except Exception as e:
            return FasResult(False, error=f"FasError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMeFasEngine", "verifications": self.verifications, "status": "Operational"}
