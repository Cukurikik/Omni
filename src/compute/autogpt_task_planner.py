# OMNI Compute Layer - AutoGPT Task Planner
class AutoGPTError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def parse_llm_action_plan(llm_response: str) -> Result:
    """Parses JSON-structured action plans from AutoGPT agent response."""
    try:
        import json
        if not llm_response:
            return Result(error=AutoGPTError("Empty response"))
            
        # Simulating extraction of thought, reasoning, plan, command
        parsed = json.loads(llm_response)
        
        return Result(value={"command_name": parsed.get("command", {}).get("name")})
    except Exception as e:
        return Result(error=AutoGPTError(f"Plan parse failed: {str(e)}"))
