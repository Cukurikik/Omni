# OMNI Compute Layer - SAM Adapter Injection
class SAMAdapterError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def inject_spatial_adapters(image_embeddings: dict, mask_prompt: dict) -> Result:
    """Injects spatial adapters into Segment Anything Model (SAM) representations."""
    try:
        if not image_embeddings or not mask_prompt:
            return Result(error=SAMAdapterError("Missing embeddings or prompt"))
            
        # Simulating adapter logic
        adapted_embeddings = {"adapted": True, "channels": 256}
        
        return Result(value={"embeddings": adapted_embeddings})
    except Exception as e:
        return Result(error=SAMAdapterError(f"Adapter injection failed: {str(e)}"))
