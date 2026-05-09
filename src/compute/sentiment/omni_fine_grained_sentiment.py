"""
@omni-layer Compute | @omni-source prrao87/fine-grained-sentiment
@omni-description Fine-grained 5-class sentiment (SST-5).
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

SENTIMENT_5 = ["very_negative","negative","neutral","positive","very_positive"]

class OmniFineGrainedSentiment:
    def __init__(self, d_model=768, n_classes=5):
        self.d_model = d_model
        self.n_classes = n_classes
        self.weights = [[math.sin((i+1)*(j+1)*0.003)*0.02 for j in range(d_model)] for i in range(n_classes)]

    def classify(self, embedding: List[float]) -> OmniResult:
        try:
            d = min(len(embedding), self.d_model)
            logits = [sum(self.weights[c][j]*embedding[j] for j in range(d)) for c in range(self.n_classes)]
            mx = max(logits); exps = [math.exp(l-mx) for l in logits]; t = sum(exps)
            probs = [e/t for e in exps]; pred = probs.index(max(probs))
            return OmniResult(data={"label":SENTIMENT_5[pred],"confidence":probs[pred],"distribution":{SENTIMENT_5[i]:probs[i] for i in range(self.n_classes)}})
        except Exception as e:
            return OmniResult(error=Exception(str(e)))

    def batch_evaluate(self, embeddings: List[List[float]], labels: List[int]) -> OmniResult:
        try:
            correct = 0; conf = [[0]*self.n_classes for _ in range(self.n_classes)]
            for emb, lbl in zip(embeddings, labels):
                r = self.classify(emb)
                if r.is_ok():
                    p = r.data["label"]; idx = SENTIMENT_5.index(p)
                    if idx == lbl: correct += 1
                    conf[lbl % self.n_classes][idx] += 1
            return OmniResult(data={"accuracy":correct/max(len(labels),1),"confusion":conf})
        except Exception as e:
            return OmniResult(error=Exception(str(e)))
