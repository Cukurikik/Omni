# Omni ProntoQA Reasoning Validator (Python)
# Compute Layer: Formal chain-of-thought validation for synthetic QA tasks.
# Ref: asaparov/prontoqa — Synthetic QA for formal CoT analysis.

from typing import List, Dict, Set, Tuple

class ProofStep:
    __slots__ = ('premise', 'conclusion', 'rule')
    def __init__(self, premise: str, conclusion: str, rule: str):
        self.premise = premise
        self.conclusion = conclusion
        self.rule = rule

def validate_proof_chain(steps: List[ProofStep], known_facts: Set[str]) -> bool:
    derived = set(known_facts)
    for step in steps:
        if step.premise not in derived:
            return False
        derived.add(step.conclusion)
    return True

def evaluate_cot_accuracy(
    predicted_chain: List[ProofStep],
    gold_chain: List[ProofStep],
    known_facts: Set[str]
) -> float:
    if not gold_chain:
        return 0.0
    pred_valid = validate_proof_chain(predicted_chain, known_facts)
    if not pred_valid:
        return 0.0
    pred_conclusions = {s.conclusion for s in predicted_chain}
    gold_conclusions = {s.conclusion for s in gold_chain}
    if not gold_conclusions:
        return 0.0
    overlap = pred_conclusions & gold_conclusions
    return round(len(overlap) / len(gold_conclusions), 6)
