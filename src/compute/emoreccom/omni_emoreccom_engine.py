from typing import Dict, Any, List
from dataclasses import dataclass
import numpy as np

# OMNI EmoRecCom Engine — Compute Layer
# Absorbing VietHoang1512/ICDAR-EmoRecCom: Multimodal Emotion Recognition on Comics.
# Implements late-fusion of text+image emotion vectors.

@dataclass
class EmoResult:
    ok: bool
    predicted_class: int = -1
    probabilities: list = None
    error: str = None

class OmniEmoRecComEngine:
    def __init__(self, text_dim: int = 768, image_dim: int = 2048, num_classes: int = 8):
        self.text_dim = text_dim
        self.image_dim = image_dim
        self.num_classes = num_classes
        self.inferences = 0
        # Mathematically initialize weight matrices with Xavier-like distribution
        scale_t = np.sqrt(2.0 / (text_dim + num_classes))
        scale_i = np.sqrt(2.0 / (image_dim + num_classes))
        np.random.seed(42)
        self.W_text = np.random.randn(text_dim, num_classes).astype(np.float32) * scale_t
        self.W_image = np.random.randn(image_dim, num_classes).astype(np.float32) * scale_i
        self.bias = np.zeros(num_classes, dtype=np.float32)

    def classify_emotion(self, text_features: np.ndarray, image_features: np.ndarray) -> EmoResult:
        if text_features.shape[-1] != self.text_dim:
            return EmoResult(False, error=f"EmoError: Text dim mismatch, expected {self.text_dim}")
        if image_features.shape[-1] != self.image_dim:
            return EmoResult(False, error=f"EmoError: Image dim mismatch, expected {self.image_dim}")
        try:
            self.inferences += 1
            text_logits = text_features @ self.W_text
            image_logits = image_features @ self.W_image
            fused_logits = (text_logits + image_logits) / 2.0 + self.bias
            # Softmax
            exp_logits = np.exp(fused_logits - np.max(fused_logits))
            probs = exp_logits / np.sum(exp_logits)
            predicted = int(np.argmax(probs))
            return EmoResult(True, predicted_class=predicted, probabilities=probs.tolist())
        except Exception as e:
            return EmoResult(False, error=f"EmoError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniEmoRecComEngine", "inferences": self.inferences,
                "num_classes": self.num_classes, "status": "Operational"}
