# Omni KnowPAT Knowledge Preference Alignment
# Ref: zjukg/KnowPAT — ACL 2024 Findings
from typing import List, Dict
import math

def dpo_loss(chosen_logprob: float, rejected_logprob: float, beta: float = 0.1) -> float:
    diff = beta * (chosen_logprob - rejected_logprob)
    return round(-math.log(1 / (1 + math.exp(-diff)) + 1e-10), 6)

def knowledge_augmented_reward(answer: str, kg_facts: List[str]) -> float:
    answer_tokens = set(answer.lower().split())
    coverage = 0
    for fact in kg_facts:
        fact_tokens = set(fact.lower().split())
        if fact_tokens & answer_tokens: coverage += 1
    return round(coverage / max(len(kg_facts), 1), 4)

def preference_pair_quality(chosen_score: float, rejected_score: float, margin: float = 0.1) -> Dict:
    gap = chosen_score - rejected_score
    return {"gap": round(gap, 4), "valid": gap > margin, "quality": "high" if gap > 0.5 else "medium" if gap > margin else "low"}

def build_preference_dataset(qa_pairs: List[Dict], kg_facts: Dict) -> List[Dict]:
    dataset = []
    for qa in qa_pairs:
        q = qa.get("question", "")
        facts = kg_facts.get(q, [])
        r_chosen = knowledge_augmented_reward(qa.get("chosen", ""), facts)
        r_rejected = knowledge_augmented_reward(qa.get("rejected", ""), facts)
        dataset.append({"question": q, "chosen_reward": r_chosen, "rejected_reward": r_rejected})
    return dataset
