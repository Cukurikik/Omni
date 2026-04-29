# Omni FLASK Fine-Grained Evaluator
# Ref: kaistAI/FLASK — ICLR 2024 Spotlight
# Implements: Skill-based LLM evaluation with 12 alignment skills
from typing import List, Dict

SKILLS = ["logical_thinking", "background_knowledge", "problem_handling", "creativity",
          "metacognition", "comprehension", "insightfulness", "completeness",
          "conciseness", "readability", "harmlessness", "robustness"]

def evaluate_response(scores: Dict[str, float]) -> Dict:
    valid = {k: v for k, v in scores.items() if k in SKILLS and 1 <= v <= 5}
    if not valid: return {"error": "no valid skill scores"}
    avg = sum(valid.values()) / len(valid)
    return {"skill_scores": valid, "overall": round(avg, 4), "n_skills": len(valid),
            "primary_dimension": _classify_dimension(valid)}

def _classify_dimension(scores: Dict[str, float]) -> str:
    dims = {"logical": ["logical_thinking", "problem_handling"],
            "factual": ["background_knowledge", "comprehension"],
            "creative": ["creativity", "insightfulness"],
            "safety": ["harmlessness", "robustness"]}
    best_dim, best_avg = "unknown", 0
    for dim, skills in dims.items():
        vals = [scores[s] for s in skills if s in scores]
        if vals:
            avg = sum(vals) / len(vals)
            if avg > best_avg: best_avg = avg; best_dim = dim
    return best_dim

def aggregate_evaluations(evals: List[Dict]) -> Dict:
    all_scores = {s: [] for s in SKILLS}
    for e in evals:
        for s, v in e.get("skill_scores", {}).items():
            all_scores[s].append(v)
    return {s: round(sum(v)/len(v), 4) if v else 0 for s, v in all_scores.items()}
