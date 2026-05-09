"""OMNI Compute — Zero-Shot BERT Adapters for Intent Detection"""
import logging
from typing import List, Dict

logger = logging.getLogger("omni.zero_shot_adapters")

class ZeroShotBERTAdapter:
    """
    Z-BERT-A: Zero-Shot pipeline for Unknown Intent Detection.
    Uses adapter modules to fine-tune without catastrophic forgetting,
    and detects out-of-domain/unknown intents.
    """
    def __init__(self, known_intents: List[str], threshold: float = 0.5):
        self.known_intents = known_intents
        self.threshold = threshold
        # Simulated Adapter Weights for each known intent
        self.adapters = {intent: [0.1] * 64 for intent in known_intents}
        logger.info(f"Initialized Zero-Shot BERT Adapter with {len(known_intents)} known intents")

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        return dot / (norm1 * norm2 + 1e-9)

    def extract_features(self, text: str) -> List[float]:
        """Simulate transformer + adapter feature extraction."""
        base_feature = [ord(c)*0.01 for c in text[:64]]
        if len(base_feature) < 64:
            base_feature.extend([0.0] * (64 - len(base_feature)))
        return base_feature

    def detect_intent(self, text: str) -> Dict[str, Any]:
        """
        Classifies into known intent or identifies as 'UNKNOWN'
        if confidence is below threshold.
        """
        features = self.extract_features(text)
        
        similarities = {}
        for intent, adapter_weights in self.adapters.items():
            # Apply adapter
            adapted_features = [f * w for f, w in zip(features, adapter_weights)]
            # Target cluster center (simulated)
            target = [1.0] * 64
            sim = self._cosine_similarity(adapted_features, target)
            similarities[intent] = sim
            
        best_intent = max(similarities, key=similarities.get)
        best_score = similarities[best_intent]
        
        if best_score < self.threshold:
            return {
                "intent": "UNKNOWN_INTENT",
                "confidence": round(1.0 - best_score, 4),
                "is_known": False,
                "closest_known": best_intent
            }
            
        return {
            "intent": best_intent,
            "confidence": round(best_score, 4),
            "is_known": True
        }
