# Omni PanelGPT Multi-Expert Prompting Engine
# Ref: holarissun/PanelGPT — zero-shot panel discussion
from typing import List, Dict

PANEL_TEMPLATE = """Several experts are asked to answer this question. Each expert provides an independent answer, then they discuss and reach a consensus.

Question: {question}

Expert 1 ({role1}): {answer1}
Expert 2 ({role2}): {answer2}
Expert 3 ({role3}): {answer3}

After discussion, the consensus answer is:"""

def build_panel_prompt(question: str, roles: List[str] = None) -> str:
    if roles is None:
        roles = ["Mathematician", "Logician", "Scientist"]
    roles = (roles + ["Expert"])[:3]
    return PANEL_TEMPLATE.format(question=question, role1=roles[0], role2=roles[1], role3=roles[2], answer1="[Expert 1 reasoning]", answer2="[Expert 2 reasoning]", answer3="[Expert 3 reasoning]")

def panel_consistency(expert_answers: List[str]) -> float:
    if len(expert_answers) < 2: return 1.0
    tokens = [set(a.lower().split()) for a in expert_answers]
    pairs = 0; overlap = 0
    for i in range(len(tokens)):
        for j in range(i+1, len(tokens)):
            pairs += 1
            overlap += len(tokens[i] & tokens[j]) / max(len(tokens[i] | tokens[j]), 1)
    return round(overlap / max(pairs, 1), 4)

def evaluate_panel(baseline_acc: float, panel_acc: float) -> Dict:
    return {"baseline": round(baseline_acc,4), "panel": round(panel_acc,4), "improvement": round(panel_acc - baseline_acc, 4)}
