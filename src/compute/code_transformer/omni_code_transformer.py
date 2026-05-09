"""
@omni-layer Compute | @omni-source danielzuegner/code-transformer
@omni-description Language-agnostic code representation learning from AST structure.
Multi-relational attention over code tokens with relative position encoding.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniCodeTransformer:
    """AST-aware transformer for language-agnostic code representation."""
    RELATION_TYPES = ["child", "parent", "sibling", "next_leaf", "prev_leaf", "same_scope", "data_flow"]

    def __init__(self, d_model: int = 256, n_heads: int = 4, n_layers: int = 4, n_relations: int = 7):
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.n_relations = n_relations

    def _relational_attention(self, queries: List[List[float]], keys: List[List[float]], values: List[List[float]], relation_matrix: List[List[int]]) -> List[List[float]]:
        d = len(queries[0]) if queries else 1
        scale = math.sqrt(d)
        n = len(queries)
        output = []
        for i in range(n):
            scores = []
            for j in range(n):
                content_score = sum(queries[i][dd]*keys[j][dd] for dd in range(min(d,16))) / scale
                rel_type = relation_matrix[i][j] if i < len(relation_matrix) and j < len(relation_matrix[i]) else 0
                rel_bias = math.sin(rel_type * 0.5) * 0.1
                scores.append(content_score + rel_bias)
            max_s = max(scores) if scores else 0
            exp_s = [math.exp(s-max_s) for s in scores]
            total = sum(exp_s) + 1e-8
            w = [e/total for e in exp_s]
            out = [sum(w[j]*values[j][dd] for j in range(n)) for dd in range(d)]
            output.append(out)
        return output

    def encode_ast(self, token_embeddings: List[List[float]], relation_matrix: List[List[int]]) -> OmniResult:
        try:
            if not token_embeddings:
                return OmniResult(error=Exception("Empty tokens"))
            hidden = token_embeddings
            for layer in range(self.n_layers):
                hidden = self._relational_attention(hidden, hidden, hidden, relation_matrix)
                hidden = [[h[d] + math.tanh(h[d]*0.1)*0.01 for d in range(self.d_model)] for h in hidden]
            pooled = [sum(hidden[t][d] for t in range(len(hidden)))/len(hidden) for d in range(self.d_model)]
            return OmniResult(data={"code_embedding": pooled[:16], "n_tokens": len(hidden), "n_layers": self.n_layers, "n_relations": self.n_relations})
        except Exception as e:
            return OmniResult(error=Exception(f"AST encoding failed: {e}"))

    def method_name_prediction(self, code_embedding: List[float], vocab_size: int = 10000) -> OmniResult:
        try:
            logits = [sum(code_embedding[j]*math.sin((j+1)*(v+1)*0.0001) for j in range(min(len(code_embedding),16))) for v in range(min(vocab_size, 128))]
            max_l = max(logits)
            exp_l = [math.exp(l-max_l) for l in logits]
            total = sum(exp_l)
            probs = [e/total for e in exp_l]
            top_k = sorted(range(len(probs)), key=lambda i: -probs[i])[:5]
            return OmniResult(data={"top_predictions": [{"vocab_id": i, "prob": probs[i]} for i in top_k]})
        except Exception as e:
            return OmniResult(error=Exception(f"Prediction failed: {e}"))
