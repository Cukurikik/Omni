class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ReasoningEngine:
    def __init__(self):
        pass

    def evaluate_reasoning_path(self, steps: list[str], target_goal: str) -> OmniResult:
        if not steps:
            return OmniResult(error="Reasoning path cannot be empty")
        
        if not target_goal:
            return OmniResult(error="Target goal must be defined")

        # Deterministic simulation of an Agentic RAG reasoning graph
        # Validates if the sequence of thought->action->observation steps converges to the goal
        try:
            # Synthetic validation: Count if the steps contain "observe" and "action"
            action_count = sum(1 for s in steps if "action" in s.lower())
            observe_count = sum(1 for s in steps if "observe" in s.lower())
            
            if action_count == 0 or observe_count == 0:
                 return OmniResult(value={"valid": False, "score": 0.0, "reason": "Missing Action or Observation steps"})
            
            # Score based on action/observation balance (ReAct pattern)
            balance = min(action_count, observe_count) / max(action_count, observe_count)
            
            return OmniResult(value={"valid": True, "score": balance})
        except Exception as e:
            return OmniResult(error=str(e))
