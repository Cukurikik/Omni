# Omni WKM (World Knowledge Model) Planning Engine
# Ref: zjunlp/WKM
from typing import List, Dict, Tuple

def simulate_world_state_transition(current_state: Dict[str, float], action: Dict[str, float]) -> Dict[str, float]:
    new_state = dict(current_state)
    for key, delta in action.items():
        if key in new_state:
            new_state[key] = round(new_state[key] + delta, 4)
        else:
            new_state[key] = round(delta, 4)
    return new_state

def evaluate_plan_feasibility(initial_state: Dict[str, float], plan: List[Dict[str, float]], constraints: Dict[str, float]) -> Tuple[bool, float]:
    current = dict(initial_state)
    steps_passed = 0
    
    for action in plan:
        current = simulate_world_state_transition(current, action)
        for key, max_val in constraints.items():
            if current.get(key, 0.0) > max_val:
                return False, round(steps_passed / len(plan), 4)
        steps_passed += 1
        
    return True, 1.0

def calculate_plan_reward(final_state: Dict[str, float], target_state: Dict[str, float]) -> float:
    reward = 0.0
    for key, target in target_state.items():
        val = final_state.get(key, 0.0)
        reward += 1.0 / (1.0 + abs(target - val))
    return round(reward, 4)
