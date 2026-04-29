# Omni Human-Agent Collaboration Patterns
# Ref: HenryPengZou/Awesome-Human-Agent-Collaboration — ACL 2026
from typing import List, Dict

PATTERNS = ["human_in_the_loop", "human_on_the_loop", "human_out_of_loop",
            "mixed_initiative", "shared_autonomy", "adjustable_autonomy"]

def classify_interaction(agent_actions: int, human_actions: int) -> str:
    ratio = agent_actions / max(human_actions, 1)
    if ratio < 0.5: return "human_in_the_loop"
    if ratio < 2.0: return "mixed_initiative"
    if ratio < 5.0: return "human_on_the_loop"
    return "human_out_of_loop"

def trust_calibration(accuracy_history: List[float], autonomy_level: float = 0.5) -> Dict:
    if not accuracy_history: return {"trust": 0.5, "autonomy": 0.5}
    recent = accuracy_history[-10:]
    trust = sum(recent) / len(recent)
    new_autonomy = autonomy_level + 0.1 * (trust - 0.7)
    return {"trust": round(trust, 4), "autonomy": round(max(0, min(1, new_autonomy)), 4)}

def handoff_protocol(agent_confidence: float, threshold: float = 0.6) -> Dict:
    if agent_confidence >= threshold:
        return {"action": "agent_proceed", "confidence": round(agent_confidence, 4)}
    return {"action": "escalate_to_human", "confidence": round(agent_confidence, 4)}
