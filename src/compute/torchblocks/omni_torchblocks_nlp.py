"""
@omni-layer Compute | @omni-source lonePatient/TorchBlocks
@omni-description TorchBlocks NLP toolkit: multi-task sequence classification,
token classification, and text matching with shared encoder.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniTorchBlocks:
    def __init__(self, d=768, n_classes=3, n_labels=9):
        self.d = d; self.n_classes = n_classes; self.n_labels = n_labels
        self.cls_head = [[math.sin((i+1)*(j+1)*0.01)*0.02 for j in range(n_classes)] for i in range(d)]
        self.ner_head = [[math.cos((i+1)*(j+1)*0.01)*0.02 for j in range(n_labels)] for i in range(d)]

    def encode(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        for i, ch in enumerate(text[:200]):
            idx = (ord(ch) * (i+1)) % self.d
            emb[idx] += math.tanh(ord(ch) * 0.01)
        norm = math.sqrt(sum(v*v for v in emb) + 1e-8)
        return [v/norm for v in emb]

    def classify(self, text: str) -> OmniResult:
        try:
            emb = self.encode(text)
            logits = [sum(emb[i]*self.cls_head[i][c] for i in range(self.d)) for c in range(self.n_classes)]
            max_l = max(logits); exps = [math.exp(l-max_l) for l in logits]
            total = sum(exps); probs = [e/total for e in exps]
            pred = probs.index(max(probs))
            labels = ["negative", "neutral", "positive"]
            return OmniResult(data={"label": labels[pred] if pred < len(labels) else str(pred), "confidence": probs[pred], "probabilities": dict(zip(labels, probs))})
        except Exception as e: return OmniResult(error=e)

    def token_classify(self, tokens: List[str]) -> OmniResult:
        try:
            tag_names = ["O","B-PER","I-PER","B-ORG","I-ORG","B-LOC","I-LOC","B-MISC","I-MISC"]
            results = []
            for tok in tokens:
                emb = self.encode(tok)
                logits = [sum(emb[i]*self.ner_head[i][l] for i in range(self.d)) for l in range(self.n_labels)]
                pred = logits.index(max(logits))
                results.append({"token": tok, "tag": tag_names[pred] if pred < len(tag_names) else "O", "score": max(logits)})
            return OmniResult(data={"tags": results, "n_tokens": len(tokens)})
        except Exception as e: return OmniResult(error=e)

    def text_similarity(self, text_a: str, text_b: str) -> OmniResult:
        try:
            emb_a = self.encode(text_a); emb_b = self.encode(text_b)
            dot = sum(a*b for a, b in zip(emb_a, emb_b))
            return OmniResult(data={"similarity": dot, "label": "similar" if dot > 0.5 else "dissimilar"})
        except Exception as e: return OmniResult(error=e)
