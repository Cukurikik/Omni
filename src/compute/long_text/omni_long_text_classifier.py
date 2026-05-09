# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo mim-solutions/bert_for_longer_texts + OctoberChang/X-Transformer
# @omni-description Long text classifier: chunk-pooling BERT for texts >512
# tokens with hierarchical aggregation + extreme multi-label classification.

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class LongTextConfig:
    max_chunk: int = 512
    overlap: int = 64
    d_model: int = 768
    n_labels: int = 1000
    pool_strategy: str = "attention"  # mean, max, attention

class TextChunker:
    def __init__(self, max_chunk: int = 512, overlap: int = 64):
        self.max_chunk = max_chunk
        self.overlap = overlap
    def chunk(self, token_ids: List[int]) -> List[List[int]]:
        chunks = []
        stride = self.max_chunk - self.overlap
        for start in range(0, len(token_ids), stride):
            end = min(start + self.max_chunk, len(token_ids))
            chunks.append(token_ids[start:end])
            if end >= len(token_ids):
                break
        return chunks if chunks else [token_ids[:self.max_chunk]]

class ChunkEncoder:
    def __init__(self, d: int = 768):
        self.d = d
    def encode(self, chunk: List[int]) -> List[float]:
        emb = [0.0]*self.d
        for i, tid in enumerate(chunk[:200]):
            for d in range(min(32, self.d)):
                emb[d] += math.sin((tid+1)*(d+1)*0.0001+i*0.01)*0.01
        norm = math.sqrt(sum(e*e for e in emb))+1e-10
        return [e/norm for e in emb]

class AttentionPooler:
    def __init__(self, d: int = 768):
        self.d = d
        self.query = [math.sin(i*0.01)*0.1 for i in range(d)]
    def pool(self, chunk_embs: List[List[float]]) -> List[float]:
        n = len(chunk_embs)
        if n == 0:
            return [0.0]*self.d
        if n == 1:
            return chunk_embs[0]
        scores = []
        for emb in chunk_embs:
            s = sum(self.query[d]*emb[d] for d in range(min(32, self.d)))
            scores.append(s)
        mx = max(scores)
        exps = [math.exp(s-mx) for s in scores]
        sm = sum(exps)+1e-10
        weights = [e/sm for e in exps]
        pooled = [sum(weights[i]*chunk_embs[i][d] for i in range(n)) for d in range(self.d)]
        return pooled

class LongTextClassifier:
    def __init__(self, config: LongTextConfig):
        self.config = config
        self.chunker = TextChunker(config.max_chunk, config.overlap)
        self.encoder = ChunkEncoder(config.d_model)
        self.pooler = AttentionPooler(config.d_model)
    def classify(self, token_ids: List[int], top_k: int = 5) -> List[Tuple[int, float]]:
        chunks = self.chunker.chunk(token_ids)
        chunk_embs = [self.encoder.encode(c) for c in chunks]
        doc_emb = self.pooler.pool(chunk_embs)
        logits = [sum(doc_emb[d]*math.sin((l+1)*(d+1)*0.001) for d in range(min(32, self.config.d_model)))
                  for l in range(self.config.n_labels)]
        indexed = [(i, l) for i, l in enumerate(logits)]
        indexed.sort(key=lambda x: -x[1])
        top = indexed[:top_k]
        mx = max(v for _, v in top)
        exps = [(i, math.exp(v-mx)) for i, v in top]
        sm = sum(e for _, e in exps)+1e-10
        return [(i, e/sm) for i, e in exps]

class XTransformerMultiLabel:
    """X-Transformer extreme multi-label classification with label clustering."""
    def __init__(self, n_labels: int = 100000, n_clusters: int = 256, d: int = 768):
        self.n_labels = n_labels
        self.n_clusters = n_clusters
        self.d = d
    def predict(self, doc_emb: List[float], top_k: int = 10) -> List[Tuple[int, float]]:
        cluster_scores = [sum(doc_emb[d%len(doc_emb)]*math.sin((c+1)*(d+1)*0.0001) for d in range(16))
                         for c in range(self.n_clusters)]
        top_clusters = sorted(range(len(cluster_scores)), key=lambda c: -cluster_scores[c])[:8]
        candidates = []
        for c in top_clusters:
            labels_per_cluster = self.n_labels // self.n_clusters
            for l in range(labels_per_cluster):
                label_id = c * labels_per_cluster + l
                if label_id < self.n_labels:
                    score = cluster_scores[c] + sum(doc_emb[d%len(doc_emb)]*math.cos(label_id*0.001+d*0.01) for d in range(8))
                    candidates.append((label_id, score))
        candidates.sort(key=lambda x: -x[1])
        return candidates[:top_k]
