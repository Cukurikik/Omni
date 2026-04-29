# OMNI Compute Layer - Penzai NN Visualization
class PenzaiError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def extract_pytree_structure(model_pytree: dict) -> Result:
    """Extracts structural graph of JAX Pytree for Penzai visualization."""
    try:
        if not model_pytree:
            return Result(error=PenzaiError("Empty pytree"))
            
        nodes = []
        for key, value in model_pytree.items():
            nodes.append({"layer": key, "type": str(type(value))})
            
        return Result(value={"tree_nodes": nodes})
    except Exception as e:
        return Result(error=PenzaiError(f"Extraction failed: {str(e)}"))
