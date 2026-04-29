# Omni AttrPrompt Data Generator (Python)
# Compute Layer: Attributed training data generation with diversity control.
# Ref: yueyu1030/AttrPrompt — NeurIPS 2023, Diversity and Bias in LLM data gen.

from typing import List, Dict, Set
import hashlib

class AttributedSample:
    __slots__ = ('text', 'label', 'attributes', 'fingerprint')
    def __init__(self, text: str, label: str, attributes: Dict[str, str]):
        self.text = text
        self.label = label
        self.attributes = attributes
        raw = f"{text}|{label}|{'|'.join(f'{k}={v}' for k,v in sorted(attributes.items()))}"
        self.fingerprint = hashlib.sha256(raw.encode()).hexdigest()[:16]

def compute_diversity_score(samples: List[AttributedSample]) -> float:
    if not samples:
        return 0.0
    unique_fps = {s.fingerprint for s in samples}
    return round(len(unique_fps) / len(samples), 6)

def detect_label_bias(samples: List[AttributedSample]) -> Dict[str, float]:
    if not samples:
        return {}
    counts: Dict[str, int] = {}
    for s in samples:
        counts[s.label] = counts.get(s.label, 0) + 1
    total = len(samples)
    return {k: round(v / total, 6) for k, v in counts.items()}
