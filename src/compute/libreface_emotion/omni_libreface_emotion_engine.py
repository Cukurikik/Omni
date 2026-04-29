from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI LibreFace & BERT Emotion Engine — Compute Layer
# Absorbing XaingHui/LibreFaceAndBert2Emotion
# Fuses Action Unit (AU) face features with Text embeddings for Emotion scoring.

@dataclass
class EmotionResult:
    ok: bool
    combined_scores: np.ndarray = None
    dominant_emotion: str = ""
    error: str = None

class OmniLibreFaceEmotionEngine:
    EMOTIONS = ["Anger", "Disgust", "Fear", "Happiness", "Sadness", "Surprise", "Neutral"]

    def __init__(self, au_dim: int = 35, text_dim: int = 768):
        self.au_dim = au_dim
        self.text_dim = text_dim
        self.inferences = 0
        np.random.seed(91)
        # Fusion weights imitating cross-modal projection layer
        self.au_proj = np.random.randn(au_dim, len(self.EMOTIONS)).astype(np.float32) * 0.1
        self.text_proj = np.random.randn(text_dim, len(self.EMOTIONS)).astype(np.float32) * 0.1

    def detect_emotion(self, face_aus: np.ndarray, text_embed: np.ndarray, alpha: float = 0.6) -> EmotionResult:
        """
        Face AUs (Action Units): (au_dim,) array extracted by LibreFace.
        text_embed: (text_dim,) BERT embedding.
        alpha: weight given to facial features vs text.
        """
        if face_aus.shape != (self.au_dim,):
            return EmotionResult(False, error=f"EmotionError: Expected AU shape ({self.au_dim},)")
        if text_embed.shape != (self.text_dim,):
            return EmotionResult(False, error=f"EmotionError: Expected Text shape ({self.text_dim},)")
        
        try:
            self.inferences += 1
            # Normalize inputs
            f_norm = face_aus / max(np.linalg.norm(face_aus), 1e-8)
            t_norm = text_embed / max(np.linalg.norm(text_embed), 1e-8)

            # Project into emotion space
            f_logits = f_norm @ self.au_proj
            t_logits = t_norm @ self.text_proj

            # Weighted fusion
            combined_logits = (alpha * f_logits) + ((1.0 - alpha) * t_logits)
            
            # Softmax
            exp_logits = np.exp(combined_logits - np.max(combined_logits))
            probs = exp_logits / np.sum(exp_logits)
            
            dominant_idx = np.argmax(probs)
            return EmotionResult(True, combined_scores=probs, dominant_emotion=self.EMOTIONS[dominant_idx])
        except Exception as e:
            return EmotionResult(False, error=f"EmotionError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniLibreFaceEmotionEngine", "inferences": self.inferences, "status": "Operational"}
