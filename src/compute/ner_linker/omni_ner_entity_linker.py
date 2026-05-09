# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo weizhepei/BERT-NER + dell-research-harvard/linktransformer
# @omni-description NER + Entity Linking engine: BERT-style NER with
# BIO tagging and transformer-based entity resolution/deduplication.

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class NERConfig:
    vocab_size: int = 30522
    d_model: int = 768
    n_heads: int = 12
    n_labels: int = 9  # O, B-PER, I-PER, B-ORG, I-ORG, B-LOC, I-LOC, B-MISC, I-MISC
    max_seq_len: int = 512

LABEL_MAP = {0:"O",1:"B-PER",2:"I-PER",3:"B-ORG",4:"I-ORG",5:"B-LOC",6:"I-LOC",7:"B-MISC",8:"I-MISC"}

class TokenEmbedder:
    def __init__(self, vocab_size: int, d: int):
        self.d = d
        self.vocab_size = vocab_size
    def embed(self, token_ids: List[int]) -> List[List[float]]:
        return [[math.sin((tid+1)*(d+1)*0.001)*0.1+math.cos(pos*0.01+d*0.001)*0.05
                 for d in range(self.d)] for pos, tid in enumerate(token_ids)]

class NERClassifier:
    def __init__(self, cfg: NERConfig):
        self.cfg = cfg
        self.embedder = TokenEmbedder(cfg.vocab_size, cfg.d_model)
    def predict(self, token_ids: List[int]) -> List[Tuple[int, str, float]]:
        embs = self.embedder.embed(token_ids)
        results = []
        for i, emb in enumerate(embs):
            logits = [sum(emb[d]*math.sin((l+1)*(d+1)*0.01) for d in range(min(32,len(emb)))) for l in range(self.cfg.n_labels)]
            mx = max(logits)
            exps = [math.exp(l-mx) for l in logits]
            sm = sum(exps)+1e-10
            probs = [e/sm for e in exps]
            best = max(range(len(probs)), key=lambda k: probs[k])
            results.append((best, LABEL_MAP.get(best,"O"), probs[best]))
        return results
    def extract_entities(self, token_ids: List[int], tokens: List[str]) -> List[Dict]:
        preds = self.predict(token_ids)
        entities, current = [], None
        for i, (label_id, label, conf) in enumerate(preds):
            if label.startswith("B-"):
                if current:
                    entities.append(current)
                current = {"type": label[2:], "tokens": [tokens[i] if i<len(tokens) else ""], "start": i, "confidence": conf}
            elif label.startswith("I-") and current and current["type"] == label[2:]:
                current["tokens"].append(tokens[i] if i<len(tokens) else "")
                current["confidence"] = min(current["confidence"], conf)
            else:
                if current:
                    entities.append(current)
                    current = None
        if current:
            entities.append(current)
        return entities

class EntityLinker:
    """LinkTransformer-inspired entity resolution and deduplication."""
    def __init__(self, d: int = 768):
        self.d = d
        self.registry: Dict[str, List[float]] = {}
    def register_entity(self, name: str, embedding: List[float]) -> None:
        self.registry[name] = embedding
    def embed_text(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        for i, c in enumerate(text[:200]):
            idx = (ord(c)*(i+1)) % self.d
            emb[idx] += math.sin(ord(c)*0.1)*0.1
        norm = math.sqrt(sum(e*e for e in emb))+1e-10
        return [e/norm for e in emb]
    def link(self, mention: str, top_k: int = 3) -> List[Tuple[str, float]]:
        q = self.embed_text(mention)
        scores = []
        for name, emb in self.registry.items():
            sim = sum(q[d]*emb[d] for d in range(self.d))
            scores.append((name, sim))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]
    def deduplicate(self, entities: List[str], threshold: float = 0.8) -> List[List[str]]:
        embs = {e: self.embed_text(e) for e in entities}
        clusters, visited = [], set()
        for e in entities:
            if e in visited:
                continue
            cluster = [e]
            visited.add(e)
            for other in entities:
                if other not in visited:
                    sim = sum(embs[e][d]*embs[other][d] for d in range(self.d))
                    if sim >= threshold:
                        cluster.append(other)
                        visited.add(other)
            clusters.append(cluster)
        return clusters
