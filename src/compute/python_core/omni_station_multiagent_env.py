# Omni Station Multi-Agent Env
# Ref: dualverse-ai/station — Apache-2.0
import math
from typing import Dict, List

def agent_step(position: List[float], velocity: List[float], dt: float = 0.1) -> List[float]:
    return [round(p + v * dt, 6) for p, v in zip(position, velocity)]

def agent_interact(a1: Dict, a2: Dict) -> Dict:
    dist = math.sqrt(sum((a - b)**2 for a, b in zip(a1["pos"], a2["pos"])))
    can_interact = dist < a1.get("radius", 1.0) + a2.get("radius", 1.0)
    return {"distance": round(dist, 4), "interactable": can_interact}

def environment_tick(agents: List[Dict], dt: float = 0.1) -> List[Dict]:
    return [{"id": a["id"], "pos": agent_step(a["pos"], a.get("vel", [0]*len(a["pos"])), dt)}
            for a in agents]
