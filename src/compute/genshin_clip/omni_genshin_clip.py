from typing import Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np

# OMNI Genshin CLIP Engine — Compute Layer
# Absorbing mrzjy/GenshinCLIP: SigLIP model alignment.
# Image-Text SigLIP pairwise contrastive loss evaluation mapping.

@dataclass
class SiglipResult:
    ok: bool
    temperature_scaled_logits: np.ndarray = None
    error: str = None

class OmniGenshinClipEngine:
    def __init__(self, init_temperature: float = 10.0, init_bias: float = -10.0):
        self.temperature = init_temperature
        self.bias = init_bias
        self.matches = 0

    def compute_siglip_loss_logits(self, image_embeddings: np.ndarray, text_embeddings: np.ndarray) -> SiglipResult:
        """
        image_embeddings: (B1, D)
        text_embeddings: (B2, D)
        SigLIP avoids softmax by using pairwise sigmoid loss across all pairs.
        We return the temperature scaled dot products ready for BCE.
        """
        if image_embeddings.ndim != 2 or text_embeddings.ndim != 2:
            return SiglipResult(False, error="SiglipError: Embeddings must be 2D matrices")
        if image_embeddings.shape[1] != text_embeddings.shape[1]:
            return SiglipResult(False, error="SiglipError: Dimension mismatch")
            
        try:
            self.matches += 1
            
            # Normalize
            i_norm = image_embeddings / np.maximum(np.linalg.norm(image_embeddings, axis=-1, keepdims=True), 1e-8)
            t_norm = text_embeddings / np.maximum(np.linalg.norm(text_embeddings, axis=-1, keepdims=True), 1e-8)
            
            # Pairwise dot product (B1, B2)
            logits = np.matmul(i_norm, t_norm.T)
            
            # Scale and bias
            scaled_logits = (logits * self.temperature) + self.bias
            
            return SiglipResult(True, temperature_scaled_logits=scaled_logits)
        except Exception as e:
            return SiglipResult(False, error=f"SiglipError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniGenshinClipEngine", "pairwise_matches": self.matches, "status": "Operational"}
