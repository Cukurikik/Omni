# OMNI Compute Layer - MaxText JAX LLM Trainer
class MaxTextError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def configure_mesh_sharding(batch: int, sequence: int, d_model: int) -> Result:
    """Configures TPU mesh sharding rules for MaxText."""
    try:
        if batch <= 0 or d_model <= 0:
            return Result(error=MaxTextError("Invalid tensor dimensions"))
            
        sharding_rules = {
            "activation": ("data", "fsdp", "tensor"),
            "weight": ("fsdp", "tensor", None)
        }
        
        return Result(value={"sharding_rules": sharding_rules})
    except Exception as e:
        return Result(error=MaxTextError(f"Mesh config failed: {str(e)}"))
