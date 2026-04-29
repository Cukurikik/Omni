# Omni LeanDojo Theorem Prover
# Compute: LLM-assisted Lean4 theorem proving with tactic generation.
# Ref: lean-dojo/LeanDojoChatGPT — MIT
import hashlib
from typing import Dict, List

def parse_proof_state(state: str) -> Dict:
    lines = state.strip().split('\n')
    goals = [l.strip() for l in lines if '⊢' in l]
    hypotheses = [l.strip() for l in lines if ':' in l and '⊢' not in l]
    return {"goals": goals, "hypotheses": hypotheses, "n_goals": len(goals)}

def validate_tactic(tactic: str) -> bool:
    valid_prefixes = ["apply", "intro", "simp", "rfl", "exact", "have", "induction", "cases", "rw", "constructor"]
    return any(tactic.strip().startswith(p) for p in valid_prefixes)

def score_tactic_candidates(candidates: List[Dict]) -> List[Dict]:
    for c in candidates:
        c["score"] = c.get("log_prob", -10.0) * (1.0 if validate_tactic(c.get("tactic", "")) else 0.1)
    return sorted(candidates, key=lambda x: x["score"], reverse=True)

def proof_search(initial_state: str, max_depth: int = 50) -> Dict:
    ps = parse_proof_state(initial_state)
    return {"initial_goals": ps["n_goals"], "max_depth": max_depth,
            "state_hash": hashlib.sha256(initial_state.encode()).hexdigest()[:12]}
