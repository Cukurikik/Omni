from typing import List, Dict, Any

class OmniAgentBenchEval:
    """OMNI Compute Layer: AgentBench Autonomy Evaluator"""
    
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps

    def evaluate_trajectory(self, environment_id: str, action_log: List[str]) -> Dict[str, Any]:
        if not action_log:
            return {"score": 0.0, "completion_rate": 0.0}
            
        # Deterministic scoring logic
        valid_actions = [a for a in action_log if not a.startswith("ERROR")]
        completion = len(valid_actions) / min(self.max_steps, max(1, len(action_log)))
        
        score = completion * 100.0 if "success" in action_log[-1].lower() else completion * 50.0
        
        return {
            "environment_id": environment_id,
            "score": float(score),
            "completion_rate": float(completion),
            "steps_taken": len(action_log)
        }
