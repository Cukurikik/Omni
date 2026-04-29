# Omni MachineSoM Agent Collaboration
# Compute: Society of Mind collaboration mechanisms for LLM agents.
# Ref: zjunlp/MachineSoM — ACL 2024, MIT
from typing import Dict, List

def majority_vote(responses: List[str]) -> Dict:
    counts = {}
    for r in responses: counts[r] = counts.get(r, 0) + 1
    winner = max(counts, key=counts.get) if counts else ""
    total = len(responses)
    return {"answer": winner, "confidence": round(counts.get(winner, 0) / max(total, 1), 6), "n_agents": total}

def debate_round(positions: List[Dict]) -> List[Dict]:
    avg_conf = sum(p.get("confidence", 0) for p in positions) / max(len(positions), 1)
    updated = []
    for p in positions:
        if p.get("confidence", 0) < avg_conf:
            p["revised"] = True; p["confidence"] = min(p.get("confidence", 0) * 1.2, 1.0)
        else:
            p["revised"] = False
        updated.append(p)
    return updated

def conformity_score(agent_answer: str, group_answers: List[str]) -> float:
    if not group_answers: return 0.0
    matches = sum(1 for a in group_answers if a == agent_answer)
    return round(matches / len(group_answers), 6)
