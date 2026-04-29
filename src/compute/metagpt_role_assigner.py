# OMNI Compute Layer - MetaGPT Role Assigner
class MetaGPTError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def assign_agent_roles(task_description: str, available_roles: list) -> Result:
    """Assigns software company roles to agents based on MetaGPT SOPs."""
    try:
        if not task_description:
            return Result(error=MetaGPTError("Task description is required"))
            
        # Simplified role extraction simulation
        assigned = []
        if "design" in task_description.lower():
            assigned.append("Architect")
        if "code" in task_description.lower():
            assigned.append("Engineer")
            
        if not assigned:
            assigned = ["ProductManager"]
            
        return Result(value={"assigned_roles": assigned})
    except Exception as e:
        return Result(error=MetaGPTError(f"Role assignment failed: {str(e)}"))
