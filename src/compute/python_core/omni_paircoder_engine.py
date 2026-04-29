# Omni PairCoder Multi-Plan Engine
# Ref: nju-websoft/PairCoder — ASE'24 Distinguished Paper
from typing import List, Dict

def generate_plans(problem: str, n_plans: int = 3) -> List[Dict]:
    plans = []
    strategies = ["divide_and_conquer", "brute_force", "greedy", "dp", "graph_search"]
    for i in range(min(n_plans, len(strategies))):
        plans.append({"plan_id": i, "strategy": strategies[i],
                       "confidence": round(0.9 - i * 0.15, 2)})
    return plans

def select_best_plan(plans: List[Dict], feedback: List[Dict]) -> Dict:
    if not plans: return {}
    for p in plans:
        fb = [f for f in feedback if f.get("plan_id") == p["plan_id"]]
        p["feedback_score"] = sum(f.get("pass", 0) for f in fb) / max(len(fb), 1)
    return max(plans, key=lambda p: p.get("feedback_score", 0) * p.get("confidence", 0))

def refine_code(code: str, error_msg: str) -> str:
    if "IndexError" in error_msg:
        return code.replace("arr[i]", "arr[i] if i < len(arr) else None")
    return code
