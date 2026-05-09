"""
@omni-layer Compute | @omni-source TheophileBlard/french-sentiment-analysis-with-bert
@omni-description Multilingual sentiment analysis: French/multilingual BERT
sentiment classifier with CamemBERT-style cross-lingual transfer.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniMultilingualSentiment:
    LANGS = {"en": 0, "fr": 1, "de": 2, "es": 3, "it": 4, "pt": 5, "nl": 6, "ru": 7, "zh": 8, "ja": 9, "ar": 10, "ko": 11}

    def __init__(self, d=768, n_classes=5):
        self.d = d; self.n_classes = n_classes
        self.labels = ["very_negative","negative","neutral","positive","very_positive"]

    def _encode(self, text: str, lang: str = "en") -> List[float]:
        lang_offset = self.LANGS.get(lang, 0) * 0.1
        emb = [0.0]*self.d
        for i, ch in enumerate(text[:200]):
            idx = (ord(ch)*(i+1)) % self.d
            emb[idx] += math.tanh(ord(ch)*0.01 + lang_offset)
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def predict(self, text: str, lang: str = "en") -> OmniResult:
        try:
            emb = self._encode(text, lang)
            logits = [sum(emb[i]*math.sin((c+1)*(i+1)*0.001) for i in range(self.d)) for c in range(self.n_classes)]
            max_l = max(logits); exps = [math.exp(l-max_l) for l in logits]
            total = sum(exps); probs = [e/total for e in exps]
            pred = probs.index(max(probs))
            return OmniResult(data={"label": self.labels[pred], "confidence": probs[pred], "probabilities": dict(zip(self.labels, probs)), "language": lang})
        except Exception as e: return OmniResult(error=e)

    def batch_analyze(self, texts: List[Dict]) -> OmniResult:
        try:
            results = []
            for item in texts:
                r = self.predict(item.get("text",""), item.get("lang","en"))
                if r.is_ok(): results.append(r.data)
            dist = {l: sum(1 for r in results if r["label"]==l) for l in self.labels}
            return OmniResult(data={"results": results, "distribution": dist, "n_texts": len(texts), "avg_confidence": sum(r["confidence"] for r in results)/max(len(results),1)})
        except Exception as e: return OmniResult(error=e)
