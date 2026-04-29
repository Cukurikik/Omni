# Omni Satori COAT Reasoner
# Ref: satori-reasoning/Satori — ICML'25
# Implements: Chain-of-Action-Thought (continue/reflect/explore), RAE reward
import math
from typing import List, Dict

COAT_ACTIONS = {"continue": 0, "reflect": 1, "explore": 2}

def select_action(confidence: float, step: int, max_steps: int,
                   reflect_thresh: float = 0.4, explore_thresh: float = 0.2) -> str:
    if confidence < explore_thresh and step > max_steps // 2:
        return "explore"
    if confidence < reflect_thresh:
        return "reflect"
    return "continue"

def coat_reward(is_correct: bool, n_steps: int, max_steps: int,
                efficiency_weight: float = 0.1) -> float:
    correctness = 1.0 if is_correct else -0.5
    efficiency = efficiency_weight * (1.0 - n_steps / max(max_steps, 1))
    return round(correctness + efficiency, 6)

def restart_and_explore(trajectories: List[Dict], threshold: float = 0.3) -> List[Dict]:
    promising = [t for t in trajectories if t.get("reward", 0) > threshold]
    if not promising:
        return [{"action": "explore", "from_step": 0, "reason": "all_below_threshold"}]
    best = max(promising, key=lambda t: t.get("reward", 0))
    return [{"action": "continue_from", "from_step": best.get("step", 0),
             "base_reward": best.get("reward", 0)}]

def run_coat_episode(question: str, max_steps: int = 10) -> Dict:
    trajectory = []; confidence = 0.1
    for step in range(max_steps):
        action = select_action(confidence, step, max_steps)
        if action == "reflect": confidence = min(confidence * 1.3, 1.0)
        elif action == "explore": confidence = 0.15
        else: confidence = min(confidence + 0.12, 1.0)
        trajectory.append({"step": step, "action": action, "confidence": round(confidence, 4)})
        if confidence > 0.9: break
    reward = coat_reward(confidence > 0.8, len(trajectory), max_steps)
    return {"question": question[:50], "steps": len(trajectory),
            "final_confidence": trajectory[-1]["confidence"] if trajectory else 0,
            "reward": reward, "trajectory": trajectory}
