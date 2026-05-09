"""OMNI Compute — GQA (Grouped Query Attention)"""
import math; from typing import List, Tuple, Optional

class GroupedQueryAttention:
    """GQA: fewer KV heads than query heads for memory efficiency."""
    def __init__(self, embed_dim: int, num_q_heads: int, num_kv_heads: int):
        assert num_q_heads % num_kv_heads == 0
        self.embed_dim = embed_dim; self.num_q_heads = num_q_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = embed_dim // num_q_heads
        self.kv_groups = num_q_heads // num_kv_heads
        self.scale = 1.0 / math.sqrt(self.head_dim)
    def forward(self, q_per_head: List[List[float]], k_per_head: List[List[float]],
                v_per_head: List[List[float]]) -> List[List[float]]:
        outputs = []
        for qh in range(self.num_q_heads):
            kv_idx = qh // self.kv_groups
            q = q_per_head[qh]; k = k_per_head[kv_idx]; v = v_per_head[kv_idx]
            score = sum(qi * ki for qi, ki in zip(q, k)) * self.scale
            weight = 1.0 / (1.0 + math.exp(-score))  # sigmoid approx
            out = [weight * vi for vi in v]
            outputs.append(out)
        return outputs
    def memory_savings(self) -> str:
        mha_kv = self.num_q_heads * self.head_dim * 2
        gqa_kv = self.num_kv_heads * self.head_dim * 2
        savings = (1 - gqa_kv / mha_kv) * 100
        return f"KV memory: MHA={mha_kv} vs GQA={gqa_kv} ({savings:.0f}% savings)"
    def info(self) -> dict:
        return {"q_heads": self.num_q_heads, "kv_heads": self.num_kv_heads,
                "groups": self.kv_groups, "head_dim": self.head_dim}
