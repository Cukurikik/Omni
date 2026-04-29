# Omni FollowBench Evaluator
# Ref: YJiangcm/FollowBench — ACL 2024
from typing import Dict, List
def check_constraint(response: str, constraint: Dict) -> bool:
    kw = constraint.get("keyword", "").lower()
    return kw in response.lower() if kw else True
def evaluate_following(response: str, constraints: List[Dict]) -> Dict:
    results = [check_constraint(response, c) for c in constraints]
    s = sum(results)
    return {"total": len(constraints), "satisfied": s, "csr": round(s / max(len(constraints), 1), 6)}
