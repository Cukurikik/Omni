# Omni Sentiment Reasoning Engine (Python)
# Compute Layer: Healthcare sentiment analysis with chain-of-thought reasoning.
# Ref: leduckhai/Sentiment-Reasoning — ACL 2025 Industry Track.

from typing import List, Dict, Tuple
import math

SENTIMENT_LABELS = ['positive', 'negative', 'neutral', 'mixed']

class SentimentResult:
    __slots__ = ('label', 'confidence', 'reasoning_chain', 'audio_features')
    def __init__(self, label: str, confidence: float, reasoning_chain: str, audio_features: List[float]):
        self.label = label
        self.confidence = max(0.0, min(1.0, confidence))
        self.reasoning_chain = reasoning_chain
        self.audio_features = audio_features

def classify_sentiment(logits: List[float]) -> SentimentResult:
    if not logits or len(logits) != len(SENTIMENT_LABELS):
        return SentimentResult('neutral', 0.0, 'EMPTY_LOGITS', [])
    exp_logits = [math.exp(l) for l in logits]
    total = sum(exp_logits)
    probs = [e / total for e in exp_logits]
    max_idx = probs.index(max(probs))
    label = SENTIMENT_LABELS[max_idx]
    return SentimentResult(label, round(probs[max_idx], 6), f'argmax({max_idx})', [])

def aggregate_multimodal_sentiment(
    text_logits: List[float],
    audio_logits: List[float],
    alpha: float = 0.6
) -> SentimentResult:
    if len(text_logits) != len(audio_logits):
        return classify_sentiment(text_logits)
    fused = [alpha * t + (1 - alpha) * a for t, a in zip(text_logits, audio_logits)]
    return classify_sentiment(fused)
