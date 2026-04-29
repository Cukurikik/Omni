# Omni CAMEL Multi-Agent Orchestrator
# Ref: camel-ai/multi-agent-streamlit-ui
# Implements: Role-based multi-agent task decomposition and message routing
from typing import List, Dict

ROLES = {"user_proxy": 0, "assistant": 1, "critic": 2, "planner": 3}

def create_agent(name: str, role: str, system_prompt: str) -> Dict:
    return {"name": name, "role": role, "system_prompt": system_prompt, "history": []}

def route_message(message: str, agents: List[Dict], current_role: str) -> str:
    role_order = ["planner", "assistant", "critic", "user_proxy"]
    idx = role_order.index(current_role) if current_role in role_order else 0
    return role_order[(idx + 1) % len(role_order)]

def decompose_task(task: str, n_subtasks: int = 3) -> List[Dict]:
    words = task.split()
    chunk = max(len(words) // n_subtasks, 1)
    return [{"id": i, "description": " ".join(words[i*chunk:(i+1)*chunk]),
             "status": "pending"} for i in range(n_subtasks)]

def consensus_check(responses: List[str]) -> Dict:
    unique = set(r.strip().lower() for r in responses)
    agreement = 1.0 - (len(unique) - 1) / max(len(responses), 1)
    return {"agreement": round(agreement, 4), "consensus": agreement > 0.6,
            "unique_responses": len(unique)}
