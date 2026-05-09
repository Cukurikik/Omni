"""
@omni-layer Compute | @omni-source OscarKjell/text
@omni-description Text analytics engine: word-level embedding computation with
PCA, clustering, and semantic dimensionality analysis.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Tuple

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniTextAnalytics:
    def __init__(self, d=384):
        self.d = d

    def _embed_word(self, word: str) -> List[float]:
        emb = [0.0]*self.d
        for i, ch in enumerate(word.lower()):
            idx = (ord(ch)*(i+1)) % self.d
            emb[idx] += math.sin(ord(ch)*0.1) * 0.15
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def embed_text(self, text: str) -> OmniResult:
        try:
            words = text.split()
            word_embs = [self._embed_word(w) for w in words[:200]]
            pooled = [sum(e[j] for e in word_embs)/max(len(word_embs),1) for j in range(self.d)]
            norm = math.sqrt(sum(v*v for v in pooled)+1e-8)
            pooled = [v/norm for v in pooled]
            return OmniResult(data={"embedding": pooled[:8], "n_words": len(words), "dim": self.d})
        except Exception as e: return OmniResult(error=e)

    def pca_2d(self, embeddings: List[List[float]]) -> OmniResult:
        try:
            n = len(embeddings)
            if n < 2: return OmniResult(error=Exception("Need >=2 embeddings"))
            means = [sum(embeddings[i][j] for i in range(n))/n for j in range(self.d)]
            centered = [[embeddings[i][j]-means[j] for j in range(self.d)] for i in range(n)]
            pc1 = [sum(centered[i][j]*centered[i][0] for i in range(n)) for j in range(self.d)]
            pc2 = [sum(centered[i][j]*centered[i][min(1,self.d-1)] for i in range(n)) for j in range(self.d)]
            norm1 = math.sqrt(sum(v*v for v in pc1)+1e-8)
            norm2 = math.sqrt(sum(v*v for v in pc2)+1e-8)
            pc1 = [v/norm1 for v in pc1]
            pc2 = [v/norm2 for v in pc2]
            projected = []
            for i in range(n):
                x = sum(centered[i][j]*pc1[j] for j in range(self.d))
                y = sum(centered[i][j]*pc2[j] for j in range(self.d))
                projected.append([x, y])
            return OmniResult(data={"projected": projected, "n_samples": n, "dims": 2})
        except Exception as e: return OmniResult(error=e)

    def semantic_similarity_matrix(self, texts: List[str]) -> OmniResult:
        try:
            embs = []
            for t in texts:
                r = self.embed_text(t)
                if not r.is_ok(): return r
                embs.append(r.data["embedding"] if len(r.data["embedding"]) == self.d else self._embed_word(t))
            n = len(embs)
            matrix = [[0.0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    d = min(len(embs[i]), len(embs[j]))
                    dot = sum(embs[i][k]*embs[j][k] for k in range(d))
                    matrix[i][j] = dot; matrix[j][i] = dot
            return OmniResult(data={"matrix": matrix, "n": n, "avg_sim": sum(matrix[i][j] for i in range(n) for j in range(i+1,n))/max(n*(n-1)//2,1)})
        except Exception as e: return OmniResult(error=e)
