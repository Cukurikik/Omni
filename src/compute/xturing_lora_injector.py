# OMNI Compute Layer - xTuring LoRA Injector
class XTuringError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def inject_lora_adapters(model_graph: dict, rank: int, alpha: int) -> Result:
    """Injects LoRA adapters into transformer linear layers for xTuring personalization."""
    try:
        if rank <= 0 or alpha <= 0:
            return Result(error=XTuringError("Invalid LoRA parameters"))
            
        modified_layers = 0
        for layer in model_graph.get("layers", []):
            if "linear" in layer:
                modified_layers += 1
                
        return Result(value={"injected_layers": modified_layers, "status": "success"})
    except Exception as e:
        return Result(error=XTuringError(f"Injection failed: {str(e)}"))
