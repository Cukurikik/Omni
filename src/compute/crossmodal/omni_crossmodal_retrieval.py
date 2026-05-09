"""
@omni-layer Compute | @omni-source minimaxir/imgbeddings + md-experiments/elastic_transformers
@omni-description Cross-modal retrieval engine: text-to-image and image-to-text
retrieval with shared embedding space and contrastive alignment.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniCrossModalRetrieval:
    def __init__(self, d=512, temperature=0.07):
        self.d = d; self.temperature = temperature
        self.text_index: List[Dict] = []
        self.image_index: List[Dict] = []

    def _embed_text(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        for i, ch in enumerate(text[:200]):
            idx = (ord(ch)*(i+1)) % self.d
            emb[idx] += math.sin(ord(ch)*0.1) * 0.1
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def _embed_image(self, features: List[float]) -> List[float]:
        emb = [0.0]*self.d
        for i in range(min(len(features), self.d)):
            emb[i] = math.tanh(features[i] * 0.5)
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def index_text(self, text_id: str, text: str) -> OmniResult:
        emb = self._embed_text(text)
        self.text_index.append({"id": text_id, "emb": emb, "text": text[:100]})
        return OmniResult(data={"indexed": text_id, "total_texts": len(self.text_index)})

    def index_image(self, image_id: str, features: List[float]) -> OmniResult:
        emb = self._embed_image(features)
        self.image_index.append({"id": image_id, "emb": emb})
        return OmniResult(data={"indexed": image_id, "total_images": len(self.image_index)})

    def text_to_image(self, query_text: str, top_k: int = 5) -> OmniResult:
        try:
            q = self._embed_text(query_text)
            scored = [(e["id"], sum(q[i]*e["emb"][i] for i in range(self.d))/self.temperature) for e in self.image_index]
            scored.sort(key=lambda x: -x[1])
            return OmniResult(data={"results": [{"id": s[0], "score": s[1]} for s in scored[:top_k]]})
        except Exception as e: return OmniResult(error=e)

    def image_to_text(self, image_features: List[float], top_k: int = 5) -> OmniResult:
        try:
            q = self._embed_image(image_features)
            scored = [(e["id"], sum(q[i]*e["emb"][i] for i in range(self.d))/self.temperature, e.get("text","")) for e in self.text_index]
            scored.sort(key=lambda x: -x[1])
            return OmniResult(data={"results": [{"id": s[0], "score": s[1], "text": s[2]} for s in scored[:top_k]]})
        except Exception as e: return OmniResult(error=e)

    def contrastive_loss(self, text_embs: List[List[float]], image_embs: List[List[float]]) -> OmniResult:
        try:
            n = min(len(text_embs), len(image_embs))
            logits = [[sum(text_embs[i][k]*image_embs[j][k] for k in range(self.d))/self.temperature for j in range(n)] for i in range(n)]
            loss = 0
            for i in range(n):
                max_l = max(logits[i]); exps = [math.exp(l-max_l) for l in logits[i]]
                loss -= math.log(exps[i] / sum(exps) + 1e-8)
            return OmniResult(data={"loss": loss/max(n,1), "n_pairs": n})
        except Exception as e: return OmniResult(error=e)
