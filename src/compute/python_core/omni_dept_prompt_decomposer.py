# Omni DePT Prompt Decomposer
# Ref: ShiZhengyan/DePT — ICLR 2024
# Implements: Decomposed prompt tuning with shared+task-specific components
import math
from typing import List, Dict

def decompose_prompt(full_prompt: List[float], rank: int) -> Dict:
    d = len(full_prompt)
    shared = full_prompt[:rank]
    task_specific = full_prompt[rank:]
    return {"shared": shared, "task_specific": task_specific, "rank": rank, "dim": d}

def compose_prompt(shared: List[float], task_specific: List[float],
                    alpha: float = 0.7) -> List[float]:
    d = len(shared) + len(task_specific)
    result = [s * alpha for s in shared] + [t * (1 - alpha) for t in task_specific]
    return [round(r, 8) for r in result]

def dept_loss(output_logits: List[float], target: int, shared: List[float],
               task: List[float], lambda_orth: float = 0.01) -> float:
    probs = [math.exp(l) for l in output_logits]
    s = sum(probs) or 1; probs = [p / s for p in probs]
    ce = -math.log(max(probs[target] if target < len(probs) else 1e-9, 1e-9))
    orth = abs(sum(a * b for a, b in zip(shared[:min(len(shared), len(task))],
                                           task[:min(len(shared), len(task))])))
    return round(ce + lambda_orth * orth, 6)

def param_count(model_dim: int, prompt_len: int, rank: int) -> Dict:
    full = model_dim * prompt_len
    decomposed = model_dim * rank + model_dim * (prompt_len - rank)
    return {"full_params": full, "dept_params": decomposed,
            "reduction": round(1 - decomposed / max(full, 1), 4)}
