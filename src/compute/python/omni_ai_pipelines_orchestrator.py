from typing import Dict, Any, Callable

class OmniPipelineOrchestrator:
    """OMNI Framework AI Pipeline Execution Engine"""
    
    def __init__(self):
        self.stages = []

    def add_stage(self, name: str, operation: Callable):
        self.stages.append((name, operation))

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the pipeline sequentially."""
        current_state = payload
        for name, op in self.stages:
            try:
                current_state = op(current_state)
                current_state[f"{name}_status"] = "success"
            except Exception as e:
                return {"status": "error", "failed_stage": name, "error": str(e)}
        
        current_state["status"] = "completed"
        return current_state
