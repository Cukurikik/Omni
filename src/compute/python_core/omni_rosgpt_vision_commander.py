# Omni ROSGPT Vision Robot Commander
# Ref: bilel-bj/ROSGPT_Vision
import math
from typing import Dict, List, Tuple

def parse_command(natural_language: str) -> Dict:
    nl = natural_language.lower()
    if any(w in nl for w in ["forward", "go", "move"]): cmd = "move_forward"
    elif any(w in nl for w in ["turn left", "left"]): cmd = "turn_left"
    elif any(w in nl for w in ["turn right", "right"]): cmd = "turn_right"
    elif any(w in nl for w in ["stop", "halt"]): cmd = "stop"
    elif any(w in nl for w in ["pick", "grab", "grasp"]): cmd = "pick_object"
    else: cmd = "unknown"
    return {"command": cmd, "raw": natural_language[:100]}

def compute_velocity(distance: float, max_speed: float = 0.5) -> Tuple[float, float]:
    linear = min(distance * 0.3, max_speed)
    angular = 0.0
    return round(linear, 4), round(angular, 4)

def scene_description_to_actions(objects: List[str], goal: str) -> List[Dict]:
    actions = []
    for obj in objects:
        if obj.lower() in goal.lower():
            actions.append({"action": "approach", "target": obj})
            actions.append({"action": "pick_object", "target": obj})
    return actions if actions else [{"action": "explore", "target": "environment"}]
