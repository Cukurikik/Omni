# Omni JacobiForcing Decoder
# Compute: Diffusion-style parallel decoding via Jacobi iteration.
# Ref: hao-ai-lab/JacobiForcing — Apache-2.0
import math
from typing import List, Dict

def jacobi_iteration_step(current_tokens: List[int], logit_matrix: List[List[float]], vocab_size: int) -> List[int]:
    new_tokens = []
    for i, logits in enumerate(logit_matrix):
        if len(logits) != vocab_size: new_tokens.append(current_tokens[i] if i < len(current_tokens) else 0)
        else: new_tokens.append(max(range(vocab_size), key=lambda j: logits[j]))
    return new_tokens

def check_convergence(prev: List[int], curr: List[int]) -> bool:
    return prev == curr

def jacobi_decode(initial_tokens: List[int], logit_fn, vocab_size: int, max_iters: int = 10) -> Dict:
    tokens = list(initial_tokens)
    for step in range(max_iters):
        logits = logit_fn(tokens)
        new_tokens = jacobi_iteration_step(tokens, logits, vocab_size)
        if check_convergence(tokens, new_tokens):
            return {"tokens": new_tokens, "converged": True, "iterations": step + 1}
        tokens = new_tokens
    return {"tokens": tokens, "converged": False, "iterations": max_iters}

def compute_speedup(ar_steps: int, jacobi_iters: int) -> float:
    if jacobi_iters == 0: return 0.0
    return round(ar_steps / jacobi_iters, 4)
