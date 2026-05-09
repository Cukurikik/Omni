"""
@omni-layer Compute | @omni-source minimaxir/imgbeddings
@omni-description Image embedding engine: CLIP-style visual feature extraction
with cosine similarity search and nearest-neighbor retrieval.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniImageEmbedder:
    def __init__(self, d=512, patch_size=16, img_size=224):
        self.d = d; self.patch_size = patch_size; self.img_size = img_size
        self.n_patches = (img_size // patch_size) ** 2
        self.projection = [[math.sin((i+1)*(j+1)*0.001)*0.02 for j in range(d)] for i in range(patch_size*patch_size*3)]
        self.index: List[Dict] = []

    def embed_image(self, pixel_values: List[float]) -> OmniResult:
        try:
            n_input = min(len(pixel_values), len(self.projection))
            emb = [0.0]*self.d
            for i in range(n_input):
                for j in range(self.d):
                    emb[j] += pixel_values[i] * self.projection[i][j]
            norm = math.sqrt(sum(v*v for v in emb) + 1e-8)
            emb = [v/norm for v in emb]
            return OmniResult(data={"embedding": emb[:8], "dim": self.d, "norm": 1.0})
        except Exception as e: return OmniResult(error=e)

    def add_to_index(self, image_id: str, embedding: List[float]) -> OmniResult:
        try:
            self.index.append({"id": image_id, "emb": embedding[:self.d]})
            return OmniResult(data={"indexed": image_id, "total": len(self.index)})
        except Exception as e: return OmniResult(error=e)

    def search(self, query_emb: List[float], top_k: int = 5) -> OmniResult:
        try:
            scores = []
            for entry in self.index:
                d = min(len(query_emb), len(entry["emb"]))
                dot = sum(query_emb[i]*entry["emb"][i] for i in range(d))
                scores.append((entry["id"], dot))
            scores.sort(key=lambda x: -x[1])
            return OmniResult(data={"results": [{"id": s[0], "score": s[1]} for s in scores[:top_k]], "n_searched": len(self.index)})
        except Exception as e: return OmniResult(error=e)

    def text_image_similarity(self, text_emb: List[float], image_emb: List[float]) -> OmniResult:
        try:
            d = min(len(text_emb), len(image_emb))
            dot = sum(text_emb[i]*image_emb[i] for i in range(d))
            nt = math.sqrt(sum(v*v for v in text_emb[:d])+1e-8)
            ni = math.sqrt(sum(v*v for v in image_emb[:d])+1e-8)
            sim = dot / (nt * ni)
            return OmniResult(data={"similarity": sim, "logit_scale": math.exp(sim)})
        except Exception as e: return OmniResult(error=e)
