# Omni MOELoRA Mixture-of-Experts LoRA Engine
# Ref: liuqidong07/MOELoRA-peft — SIGIR'24, MIT
import math
from typing import List, Dict

def expert_gate(input_features: List[float], gate_weights: List[List[float]], n_experts: int) -> List[float]:
    scores = []
    for e in range(n_experts):
        s = sum(x * w for x, w in zip(input_features, gate_weights[e])) if e < len(gate_weights) else 0
        scores.append(s)
    max_s = max(scores) if scores else 0
    exps = [math.exp(s - max_s) for s in scores]
    total = sum(exps) or 1
    return [round(e / total, 6) for e in exps]

def moe_lora_forward(x: List[float], experts_a: List[List[List[float]]], experts_b: List[List[List[float]]],
                     gate_probs: List[float], rank: int = 8) -> List[float]:
    n_experts = len(gate_probs)
    out_dim = len(experts_b[0][0]) if experts_b and experts_b[0] else 0
    result = [0.0] * out_dim
    for e in range(n_experts):
        if gate_probs[e] < 1e-6: continue
        hidden = [sum(x[j] * experts_a[e][j][i] for j in range(min(len(x), len(experts_a[e])))) for i in range(rank)]
        for i in range(out_dim):
            result[i] += gate_probs[e] * sum(hidden[j] * experts_b[e][j][i] for j in range(rank))
    return [round(r, 8) for r in result]

def load_balance_loss(gate_probs_batch: List[List[float]]) -> float:
    if not gate_probs_batch: return 0
    n_experts = len(gate_probs_batch[0])
    avg_probs = [sum(gp[e] for gp in gate_probs_batch) / len(gate_probs_batch) for e in range(n_experts)]
    freq = [sum(1 for gp in gate_probs_batch if gp[e] == max(gp)) / len(gate_probs_batch) for e in range(n_experts)]
    return round(n_experts * sum(a * f for a, f in zip(avg_probs, freq)), 6)
