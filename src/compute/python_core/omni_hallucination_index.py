# Omni Hallucination Index Evaluator
# Ref: rungalileo/hallucination-index
# Implements: ChainPoll consistency, context adherence, correctness scoring
import math
from typing import List, Dict

def chainpoll_consistency(responses: List[str]) -> float:
    if len(responses) < 2: return 1.0
    unique = len(set(responses))
    return round(1.0 - (unique - 1) / len(responses), 6)

def context_adherence(response_tokens: List[str], source_tokens: List[str]) -> float:
    if not response_tokens: return 0.0
    src_set = set(source_tokens)
    grounded = sum(1 for t in response_tokens if t in src_set)
    return round(grounded / len(response_tokens), 6)

def correctness_score(predicted: str, reference: str) -> float:
    p_set = set(predicted.lower().split())
    r_set = set(reference.lower().split())
    if not r_set: return 0.0
    precision = len(p_set & r_set) / max(len(p_set), 1)
    recall = len(p_set & r_set) / len(r_set)
    if precision + recall == 0: return 0.0
    return round(2 * precision * recall / (precision + recall), 6)

def hallucination_index(models: List[Dict]) -> List[Dict]:
    ranked = []
    for m in models:
        adh = m.get("adherence", 0)
        con = m.get("consistency", 0)
        cor = m.get("correctness", 0)
        hi = round(1.0 - (0.4 * adh + 0.3 * con + 0.3 * cor), 6)
        ranked.append({"model": m.get("name", ""), "hallucination_index": hi})
    ranked.sort(key=lambda x: x["hallucination_index"])
    return ranked
