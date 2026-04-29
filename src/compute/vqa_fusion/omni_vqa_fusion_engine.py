from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI VQA Fusion Engine — Compute Layer
# Absorbing UsefGamal/Visual-Question-Answering-VQA
# Merges InceptionV3 image embeddings with LSTM question embeddings.

@dataclass
class VqaFusionResult:
    ok: bool
    predicted_answer_index: int = -1
    fusion_confidence: float = 0.0
    error: str = None

class OmniVqaFusionEngine:
    def __init__(self, vocab_size: int = 1000, fusion_dim: int = 512):
        self.vocab_size = vocab_size
        self.fusion_dim = fusion_dim
        self.fusions = 0
        np.random.seed(42)
        
        # Dense layers for dimension matching before Hadamard product
        self.img_dense = np.random.randn(2048, fusion_dim).astype(np.float32) * 0.1
        self.txt_dense = np.random.randn(1024, fusion_dim).astype(np.float32) * 0.1
        # Final classification dense
        self.classifier = np.random.randn(fusion_dim, vocab_size).astype(np.float32) * 0.1

    def infer_answer(self, image_features: np.ndarray, lstm_features: np.ndarray) -> VqaFusionResult:
        """
        image_features: (B, 2048) from Inception
        lstm_features: (B, 1024) from NLP RNN
        """
        if image_features.shape[-1] != 2048 or lstm_features.shape[-1] != 1024:
            return VqaFusionResult(False, error="VqaError: Invalid feature dimensions")
            
        try:
            self.fusions += 1
            
            # Project to common subspace
            img_proj = np.maximum(0, np.matmul(image_features, self.img_dense)) # ReLU
            txt_proj = np.maximum(0, np.matmul(lstm_features, self.txt_dense))
            
            # Point-wise multiplication (Hadamard product)
            fused = img_proj * txt_proj
            
            # To logits
            logits = np.matmul(fused, self.classifier)
            
            # Softmax
            exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
            
            # For B=1
            if probs.ndim == 2 and probs.shape[0] == 1:
                probs = probs[0]
                
            pred_idx = int(np.argmax(probs))
            conf = float(probs[pred_idx])
            
            return VqaFusionResult(True, predicted_answer_index=pred_idx, fusion_confidence=conf)
        except Exception as e:
            return VqaFusionResult(False, error=f"VqaError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniVqaFusionEngine", "fusions": self.fusions, "status": "Operational"}
