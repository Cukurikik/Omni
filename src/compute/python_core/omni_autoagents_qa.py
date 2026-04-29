# Omni AutoAgents Complex QA Engine
# Ref: AutoLLM/AutoAgents — MIT
from typing import List, Dict

def decompose_question(question: str) -> List[str]:
    connectors = [" and ", " or ", " also ", " then "]
    parts = [question]
    for conn in connectors:
        new_parts = []
        for p in parts: new_parts.extend(p.split(conn))
        parts = new_parts
    return [p.strip() for p in parts if p.strip()]

def plan_agent_steps(sub_questions: List[str]) -> List[Dict]:
    return [{"step": i+1, "question": sq, "tool": "search" if "?" in sq else "reason",
             "status": "pending"} for i, sq in enumerate(sub_questions)]

def merge_answers(answers: List[str]) -> str:
    return " Furthermore, ".join(a.strip() for a in answers if a.strip())

def confidence_weighted_vote(responses: List[Dict]) -> Dict:
    total_conf = sum(r.get("confidence", 0.5) for r in responses)
    if total_conf == 0: return {"answer": "", "confidence": 0}
    weighted = {}
    for r in responses:
        a = r.get("answer", "").strip()
        weighted[a] = weighted.get(a, 0) + r.get("confidence", 0.5)
    best = max(weighted.items(), key=lambda x: x[1])
    return {"answer": best[0], "confidence": round(best[1] / total_conf, 4)}
