"""
@omni-layer Compute | @omni-source lucidrains/CALM-pytorch
@omni-description Composition of Augmented Language Models: cross-attention bridge between
anchor and augmenting LLMs. Learns to compose capabilities of multiple models.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Optional

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class CALMError(Exception): pass

class OmniCALMAugmentedLLM:
    """Cross-attention bridge for composing anchor + augmenting LLMs."""
    def __init__(self, d_anchor: int = 768, d_augment: int = 512, n_heads: int = 8):
        self.d_anchor = d_anchor
        self.d_augment = d_augment
        self.n_heads = n_heads
        self.d_head = d_anchor // n_heads

    def _cross_attention(self, queries: List[List[float]], keys: List[List[float]], values: List[List[float]]) -> List[List[float]]:
        scale = math.sqrt(len(queries[0])) if queries else 1
        output = []
        for q in queries:
            scores = [sum(q[d]*k[d] for d in range(min(len(q), len(k)))) / scale for k in keys]
            max_s = max(scores) if scores else 0
            exp_s = [math.exp(s - max_s) for s in scores]
            total = sum(exp_s) + 1e-8
            weights = [e / total for e in exp_s]
            attended = [sum(weights[t] * values[t][d] for t in range(len(values))) for d in range(len(q))]
            output.append(attended)
        return output

    def compose_representations(self, anchor_hidden: List[List[float]], augment_hidden: List[List[float]]) -> OmniResult:
        try:
            if not anchor_hidden or not augment_hidden:
                return OmniResult(error=CALMError("Empty hidden states"))
            d = min(len(anchor_hidden[0]), len(augment_hidden[0]))
            queries = [[h[i] for i in range(d)] for h in anchor_hidden]
            keys = [[h[i] for i in range(d)] for h in augment_hidden]
            values = keys
            cross_attn_out = self._cross_attention(queries, keys, values)
            composed = []
            for i, (anchor, cross) in enumerate(zip(anchor_hidden, cross_attn_out)):
                gate_score = 1.0 / (1.0 + math.exp(-sum(anchor[j] * cross[j % len(cross)] for j in range(min(8, len(anchor))))))
                fused = [anchor[j] + gate_score * cross[j % len(cross)] for j in range(len(anchor))]
                composed.append(fused)
            return OmniResult(data={"composed": composed, "n_tokens": len(composed), "gate_example": gate_score})
        except Exception as e:
            return OmniResult(error=CALMError(f"Composition failed: {e}"))

    def compute_composition_loss(self, anchor_logits: List[float], composed_logits: List[float], targets: List[int]) -> OmniResult:
        try:
            if not anchor_logits or not composed_logits or not targets:
                return OmniResult(error=CALMError("Empty inputs"))
            def cross_entropy(logits, target):
                max_l = max(logits)
                exp_l = [math.exp(l - max_l) for l in logits]
                return -(logits[target % len(logits)] - max_l - math.log(sum(exp_l)))
            anchor_loss = sum(cross_entropy(anchor_logits, t) for t in targets) / len(targets)
            composed_loss = sum(cross_entropy(composed_logits, t) for t in targets) / len(targets)
            return OmniResult(data={"anchor_loss": anchor_loss, "composed_loss": composed_loss, "improvement": anchor_loss - composed_loss})
        except Exception as e:
            return OmniResult(error=CALMError(f"Loss failed: {e}"))
