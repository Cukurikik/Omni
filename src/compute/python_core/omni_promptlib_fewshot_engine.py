# Omni Prompt-Lib Few-Shot Engine
# Ref: reasoning-machines/prompt-lib — MIT
from typing import Dict, List
def format_few_shot_prompt(examples: List[Dict], query: str, template: str = "Q: {q}\nA: {a}") -> str:
    parts = [template.format(q=e["question"], a=e["answer"]) for e in examples if "question" in e and "answer" in e]
    parts.append(f"Q: {query}\nA:")
    return "\n\n".join(parts)
def select_exemplars(pool: List[Dict], query: str, k: int = 5) -> List[Dict]:
    scored = []
    q_tokens = set(query.lower().split())
    for ex in pool:
        overlap = len(q_tokens & set(ex.get("question","").lower().split()))
        scored.append((overlap, ex))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:k]]
