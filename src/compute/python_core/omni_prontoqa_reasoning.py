# Omni ProntoQA Logical Reasoning Engine
# Ref: asaparov/prontoqa
from typing import List, Tuple

def parse_logical_rules(rules_text: List[str]) -> List[Tuple[str, str]]:
    """Parse simple implications (If A then B) from text."""
    parsed_rules = []
    for rule in rules_text:
        rule = rule.lower()
        if "if" in rule and "then" in rule:
            parts = rule.split("then")
            condition = parts[0].replace("if", "").strip()
            conclusion = parts[1].strip().strip(".")
            parsed_rules.append((condition, conclusion))
    return parsed_rules

def forward_chaining_reasoning(facts: set, rules: List[Tuple[str, str]], target: str, max_depth: int = 10) -> bool:
    """Execute forward chaining to prove a target fact."""
    inferred_facts = set(facts)
    changed = True
    depth = 0
    
    while changed and depth < max_depth:
        changed = False
        for condition, conclusion in rules:
            if condition in inferred_facts and conclusion not in inferred_facts:
                inferred_facts.add(conclusion)
                changed = True
                if conclusion == target:
                    return True
        depth += 1
        
    return target in inferred_facts

def evaluate_reasoning_chain(predicted_chain: List[str], ground_truth_chain: List[str]) -> float:
    """Evaluate exact match of reasoning chains."""
    if not predicted_chain or not ground_truth_chain:
        return 0.0
    
    correct_steps = sum(1 for p, g in zip(predicted_chain, ground_truth_chain) if p.strip().lower() == g.strip().lower())
    return round(correct_steps / max(len(ground_truth_chain), 1), 4)
