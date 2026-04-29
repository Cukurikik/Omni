# OMNI Compute Layer - Swarm Handoff
class SwarmError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def orchestrate_handoff(current_agent: str, target_agent: str, state: dict) -> Result:
    """Executes state handoff between agents in OpenAI Swarm."""
    try:
        if not current_agent or not target_agent:
            return Result(error=SwarmError("Both source and target agents required"))
            
        new_state = state.copy()
        new_state["last_agent"] = current_agent
        new_state["active_agent"] = target_agent
        new_state["handoff_count"] = state.get("handoff_count", 0) + 1
        
        return Result(value={"handoff_successful": True, "new_state": new_state})
    except Exception as e:
        return Result(error=SwarmError(f"Handoff failed: {str(e)}"))
