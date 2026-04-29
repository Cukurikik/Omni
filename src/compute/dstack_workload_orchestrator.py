# OMNI Compute Layer - dstack Workload Orchestrator
class DStackError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def resolve_provider_requirements(gpus: int, cloud_preference: str) -> Result:
    """Matches hardware requirements with cloud providers (dstack logic)."""
    try:
        if gpus < 0:
            return Result(error=DStackError("GPU count cannot be negative"))
            
        provision_plan = {
            "instance_type": "p4d.24xlarge" if gpus >= 8 else "g4dn.xlarge",
            "provider": cloud_preference or "aws"
        }
        
        return Result(value={"plan": provision_plan})
    except Exception as e:
        return Result(error=DStackError(f"Resolution failed: {str(e)}"))
