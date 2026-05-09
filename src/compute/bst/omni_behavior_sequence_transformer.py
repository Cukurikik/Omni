"""
@omni-layer Compute | @omni-source jiwidi/Behavior-Sequence-Transformer-Pytorch
@omni-description BST for recommendation: user behavior sequence + target item attention.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniBehaviorSequenceTransformer:
    def __init__(self, d=64, n_items=10000, max_seq=50, n_heads=2, n_layers=1):
        self.d = d; self.n_items = n_items; self.max_seq = max_seq
        self.n_heads = n_heads; self.n_layers = n_layers

    def _embed(self, item_id: int) -> List[float]:
        return [math.sin((item_id+1)*(j+1)*0.005)*0.1 for j in range(self.d)]

    def _attention(self, Q, K, V):
        d = len(Q[0]); scale = math.sqrt(d); out = []
        for i, q in enumerate(Q):
            scores = [sum(q[dd]*K[j][dd] for dd in range(min(d,16)))/scale for j in range(len(K))]
            mx = max(scores) if scores else 0
            exps = [math.exp(s-mx) for s in scores]; t = sum(exps)+1e-8
            w = [e/t for e in exps]
            out.append([sum(w[j]*V[j][dd] for j in range(len(V))) for dd in range(d)])
        return out

    def predict_ctr(self, behavior_seq: List[int], target_item: int) -> OmniResult:
        try:
            if not behavior_seq:
                return OmniResult(error=Exception("Empty sequence"))
            seq_emb = [self._embed(iid) for iid in behavior_seq[-self.max_seq:]]
            target_emb = self._embed(target_item)
            for _ in range(self.n_layers):
                seq_emb = self._attention(seq_emb, seq_emb, seq_emb)
            cross = self._attention([target_emb], seq_emb, seq_emb)
            combined = cross[0] if cross else target_emb
            score = sum(combined[j]*target_emb[j] for j in range(min(self.d, len(combined))))
            ctr = 1.0 / (1.0 + math.exp(-score))
            return OmniResult(data={"ctr_score": ctr, "target_item": target_item, "seq_len": len(behavior_seq)})
        except Exception as e:
            return OmniResult(error=Exception(str(e)))
