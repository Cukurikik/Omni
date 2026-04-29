from typing import Dict

class OmniDialOpDecision:
    """OMNI Compute Layer: DialOp Decision-oriented Dialogue Environment"""
    
    def __init__(self, strict_turns: bool = True):
        self.strict_turns = strict_turns

    def step_dialogue(self, turn_history: list[str], proposed_action: str) -> Dict[str, Any]:
        if not turn_history:
            return {"valid": False, "reward": 0.0}
            
        # Deterministic logic mock for collaborative planning
        turn_count = len(turn_history)
        reward = 1.0 if turn_count > 2 and "agree" in proposed_action.lower() else -0.1
        
        return {
            "valid": True,
            "turns_taken": turn_count,
            "reward": float(reward),
            "terminated": reward > 0.0
        }
