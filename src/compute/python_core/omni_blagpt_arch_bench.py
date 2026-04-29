# Omni BlaGPT Architecture Benchmarker
# Ref: erogol/BlaGPT
# Implements: LM architecture comparison, attention variant benchmarking, perplexity
import math
from typing import List, Dict

def compute_perplexity(log_probs: List[float]) -> float:
    if not log_probs: return float('inf')
    avg_nll = -sum(log_probs) / len(log_probs)
    return round(math.exp(avg_nll), 4)

def compare_architectures(results: List[Dict]) -> List[Dict]:
    for r in results:
        r["efficiency"] = round(r.get("throughput", 1) / max(r.get("params_m", 1), 0.01), 4)
    return sorted(results, key=lambda x: x.get("perplexity", float('inf')))

def estimate_flops(seq_len: int, d_model: int, n_layers: int, n_heads: int) -> int:
    attn_flops = 4 * seq_len * seq_len * d_model * n_layers
    ffn_flops = 8 * seq_len * d_model * d_model * n_layers
    return attn_flops + ffn_flops

def position_encoding_comparison(methods: List[str], seq_len: int) -> Dict:
    costs = {"rope": seq_len * 64, "alibi": seq_len * 32, "sinusoidal": seq_len * 128,
             "learned": seq_len * 256, "nope": 0}
    return {m: {"memory": costs.get(m, seq_len * 64)} for m in methods}
