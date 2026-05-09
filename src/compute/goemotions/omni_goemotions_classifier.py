"""
@omni-layer Compute | @omni-source monologg/GoEmotions-pytorch
@omni-description Multi-label emotion classifier with 28 emotion categories.
Implements BERT-based classification with emotion taxonomy.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

EMOTION_LABELS = ["admiration","amusement","anger","annoyance","approval","caring","confusion","curiosity","desire","disappointment","disapproval","disgust","embarrassment","excitement","fear","gratitude","grief","joy","love","nervousness","optimism","pride","realization","relief","remorse","sadness","surprise","neutral"]

class OmniGoEmotionsClassifier:
    """Multi-label emotion classification across 28 GoEmotions categories."""
    def __init__(self, d_model: int = 768, n_labels: int = 28, threshold: float = 0.3):
        self.d_model = d_model
        self.n_labels = n_labels
        self.threshold = threshold
        self.classifier_weights = [[math.sin((i+1)*(j+1)*0.003) * 0.02 for j in range(d_model)] for i in range(n_labels)]
        self.classifier_bias = [math.cos(i*0.1) * 0.01 for i in range(n_labels)]

    def classify(self, pooled_output: List[float]) -> OmniResult:
        try:
            if not pooled_output:
                return OmniResult(error=Exception("Empty input"))
            logits = [sum(self.classifier_weights[i][j]*pooled_output[j] for j in range(min(len(pooled_output), self.d_model))) + self.classifier_bias[i] for i in range(self.n_labels)]
            probs = [1.0 / (1.0 + math.exp(-l)) for l in logits]
            predictions = []
            for i, p in enumerate(probs):
                if p >= self.threshold:
                    predictions.append({"label": EMOTION_LABELS[i] if i < len(EMOTION_LABELS) else f"emotion_{i}", "probability": p, "logit": logits[i]})
            predictions.sort(key=lambda x: x["probability"], reverse=True)
            return OmniResult(data={"predictions": predictions, "all_probs": {EMOTION_LABELS[i]:probs[i] for i in range(min(len(EMOTION_LABELS),self.n_labels))}, "n_detected": len(predictions)})
        except Exception as e:
            return OmniResult(error=Exception(f"Classification failed: {e}"))

    def compute_bce_loss(self, logits: List[float], targets: List[int]) -> OmniResult:
        try:
            if len(logits) != len(targets):
                return OmniResult(error=Exception("Length mismatch"))
            loss = 0.0
            for l, t in zip(logits, targets):
                sig = 1.0 / (1.0 + math.exp(-max(-50, min(50, l))))
                loss -= t * math.log(sig + 1e-8) + (1 - t) * math.log(1 - sig + 1e-8)
            return OmniResult(data={"bce_loss": loss / len(logits), "n_labels": len(logits)})
        except Exception as e:
            return OmniResult(error=Exception(f"BCE failed: {e}"))
