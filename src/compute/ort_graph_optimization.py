# OMNI Compute Layer - ORT Graph Optimization
class ORTError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def configure_session_options(optimization_level: str) -> Result:
    """Configures pykeio ORT graph optimization flags."""
    try:
        valid_levels = ["DISABLE_ALL", "ENABLE_BASIC", "ENABLE_EXTENDED", "ENABLE_ALL"]
        if optimization_level not in valid_levels:
            return Result(error=ORTError("Invalid optimization level"))
            
        options = {
            "graph_opt_level": optimization_level,
            "intra_op_num_threads": 4
        }
        
        return Result(value={"session_options": options})
    except Exception as e:
        return Result(error=ORTError(f"Config failed: {str(e)}"))
