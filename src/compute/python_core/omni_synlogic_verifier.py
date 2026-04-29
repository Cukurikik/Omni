# Omni SynLogic Verifiable Reasoning Engine
# Ref: MiniMax-AI/SynLogic — NeurIPS 2025, MIT
from typing import List, Dict

LOGIC_TASKS = ["propositional", "first_order", "constraint_satisfaction", "graph_coloring",
               "sudoku", "boolean_satisfiability", "knights_knaves", "zebra_puzzle"]

def verify_propositional(premises: List[str], conclusion: str, truth_table: Dict[str, bool]) -> bool:
    for var, val in truth_table.items():
        conclusion = conclusion.replace(var, str(val))
    try:
        return eval(conclusion.replace("AND", " and ").replace("OR", " or ").replace("NOT", " not "))
    except Exception:
        return False

def generate_sat_instance(n_vars: int, n_clauses: int, seed: int = 42) -> List[List[int]]:
    clauses = []
    for c in range(n_clauses):
        clause = []
        for _ in range(3):
            var = ((seed * (c + 1) * 2654435761) >> 16) % n_vars + 1
            sign = 1 if ((seed * (c + 1) * 2246822519) >> 17) % 2 == 0 else -1
            clause.append(sign * var)
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        clauses.append(clause)
    return clauses

def check_sat_assignment(clauses: List[List[int]], assignment: Dict[int, bool]) -> bool:
    for clause in clauses:
        satisfied = False
        for lit in clause:
            var = abs(lit)
            val = assignment.get(var, False)
            if (lit > 0 and val) or (lit < 0 and not val):
                satisfied = True; break
        if not satisfied: return False
    return True

def reasoning_accuracy(predictions: List[bool], ground_truth: List[bool]) -> Dict:
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    return {"accuracy": round(correct / max(len(ground_truth), 1), 4), "n": len(ground_truth)}
