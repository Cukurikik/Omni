# Omni GPA-LM Game Playing Agent Engine
# Ref: BAAI-Agents/GPA-LM
from typing import List, Dict

def parse_game_state(raw_observation: str) -> Dict[str, float]:
    state = {}
    tokens = raw_observation.split()
    for i in range(len(tokens) - 1):
        if tokens[i] in ["hp", "mana", "x", "y", "score"]:
            try:
                state[tokens[i]] = float(tokens[i+1])
            except ValueError:
                pass
    return state

def calculate_action_utility(action: str, current_state: Dict[str, float]) -> float:
    utility = 0.0
    if action == "attack":
        utility = current_state.get("mana", 0) * 0.5 + 10.0
    elif action == "heal":
        utility = (100.0 - current_state.get("hp", 100.0)) * 0.8
    elif action == "move":
        utility = 5.0
    return round(utility, 4)

def select_best_action(actions: List[str], current_state: Dict[str, float]) -> Dict[str, float]:
    if not actions:
        return {"action": "wait", "utility": 0.0}
        
    scored_actions = [(a, calculate_action_utility(a, current_state)) for a in actions]
    scored_actions.sort(key=lambda x: x[1], reverse=True)
    
    return {"action": scored_actions[0][0], "utility": scored_actions[0][1]}
