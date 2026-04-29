# Omni DialOp Decision Engine
# Ref: jlin816/dialop
from typing import List, Dict, Tuple

def compute_assignment_score(expertise: List[float], topics: List[float]) -> float:
    return round(sum(r * p for r, p in zip(expertise, topics)), 6)

def greedy_assign(reviewers: List[Dict], papers: List[Dict], cap: int = 3) -> List[Tuple]:
    cands = []
    for r in reviewers:
        for p in papers:
            s = compute_assignment_score(r.get("exp", []), p.get("top", []))
            cands.append((r["id"], p["id"], s))
    cands.sort(key=lambda x: x[2], reverse=True)
    out, done, load = [], set(), {}
    for rid, pid, s in cands:
        if pid in done or load.get(rid, 0) >= cap: continue
        out.append((rid, pid, s)); done.add(pid); load[rid] = load.get(rid, 0) + 1
    return out

def mediation_score(prefs: List[List[float]]) -> List[float]:
    if not prefs: return []
    n = len(prefs[0])
    return [round(sum(p[i] for p in prefs) / len(prefs), 6) for i in range(n)]
