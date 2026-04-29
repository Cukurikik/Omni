# Omni HalluQA Evaluator
# Compute: Hallucination evaluation for Chinese LLMs.
# Ref: OpenMOSS/HalluQA
import hashlib
from typing import Dict, List

def evaluate_hallucination(response: str, facts: List[str]) -> Dict:
    r_tokens = set(response.lower().split())
    supported = 0
    for f in facts:
        f_tokens = set(f.lower().split())
        if r_tokens & f_tokens:
            supported += 1
    coverage = supported / len(facts) if facts else 0.0
    return {"supported_facts": supported, "total_facts": len(facts),
            "coverage": round(coverage, 6), "hallucinated": coverage < 0.5}
