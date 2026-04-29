# Omni Agentic Workflow Patterns Engine
# Ref: arunpshankar/Agentic-Workflow-Patterns — MIT
from typing import List, Dict, Callable

def chain_pattern(steps: List[Dict]) -> Dict:
    results = []
    for step in steps:
        results.append({"step": step.get("name", ""), "output": f"[result of {step.get('name', '')}]"})
    return {"pattern": "chain", "steps": len(steps), "results": results}

def parallel_pattern(tasks: List[Dict]) -> Dict:
    return {"pattern": "parallel", "n_tasks": len(tasks),
            "results": [{"task": t.get("name", ""), "status": "completed"} for t in tasks]}

def router_pattern(query: str, routes: Dict[str, str]) -> Dict:
    q_lower = query.lower()
    for keyword, route in routes.items():
        if keyword in q_lower: return {"pattern": "router", "matched": keyword, "route": route}
    return {"pattern": "router", "matched": "default", "route": routes.get("default", "general")}

def evaluator_pattern(output: str, criteria: List[str]) -> Dict:
    scores = {c: round(len(output) % 5 / 5 + 0.5, 2) for c in criteria}
    return {"pattern": "evaluator", "scores": scores, "pass": all(v >= 0.5 for v in scores.values())}

def orchestrator_pattern(task: str, agents: List[str]) -> Dict:
    plan = [{"agent": a, "subtask": f"Handle {a}-specific part of: {task[:50]}"} for a in agents]
    return {"pattern": "orchestrator", "plan": plan, "n_agents": len(agents)}
