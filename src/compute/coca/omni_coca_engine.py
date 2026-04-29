from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    class nn: Module = object

# OMNI CoCa Engine — Compute Layer
# Absorbing lucidrains/CoCa-pytorch: Contrastive Captioners — joint contrastive + captioning loss.

@dataclass
class CocaResult:
    ok: bool
    contrastive_loss: float = 0.0
    captioning_loss: float = 0.0
    total_loss: float = 0.0
    error: str = None

class OmniCocaEngine:
    def __init__(self, embed_dim: int = 512, temperature: float = 0.07):
        self.embed_dim = embed_dim
        self.temperature = temperature
        self.trainings = 0

    def compute_contrastive_loss(self, image_embeds: np.ndarray, text_embeds: np.ndarray) -> float:
        """InfoNCE contrastive loss over batch."""
        i_norm = image_embeds / np.maximum(np.linalg.norm(image_embeds, axis=1, keepdims=True), 1e-8)
        t_norm = text_embeds / np.maximum(np.linalg.norm(text_embeds, axis=1, keepdims=True), 1e-8)
        logits = (i_norm @ t_norm.T) / self.temperature
        B = logits.shape[0]
        labels = np.arange(B)
        # Cross-entropy for image→text and text→image
        def cross_entropy(logits_row, target):
            exp = np.exp(logits_row - np.max(logits_row, axis=1, keepdims=True))
            probs = exp / np.sum(exp, axis=1, keepdims=True)
            return -np.mean(np.log(probs[np.arange(B), target] + 1e-10))
        loss_i2t = cross_entropy(logits, labels)
        loss_t2i = cross_entropy(logits.T, labels)
        return float((loss_i2t + loss_t2i) / 2.0)

    def compute_coca_loss(self, image_embeds: np.ndarray, text_embeds: np.ndarray,
                          caption_logits: np.ndarray = None) -> CocaResult:
        if image_embeds.ndim != 2 or text_embeds.ndim != 2:
            return CocaResult(False, error="CoCaError: Expected 2D embeddings")
        try:
            self.trainings += 1
            cl = self.compute_contrastive_loss(image_embeds, text_embeds)
            cap_loss = 0.0
            if caption_logits is not None:
                cap_loss = float(np.mean(np.abs(caption_logits)))  # Placeholder for CE over vocab
            total = cl + cap_loss
            return CocaResult(True, contrastive_loss=cl, captioning_loss=cap_loss, total_loss=total)
        except Exception as e:
            return CocaResult(False, error=f"CoCaError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniCocaEngine", "trainings": self.trainings,
                "temperature": self.temperature, "status": "Operational"}
