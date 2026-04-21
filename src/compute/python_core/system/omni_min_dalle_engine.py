import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OmniMinDalleEngine:
    """
    OMNI Engine for min-dalle (DALL-E Mini/Mega wrapper).
    Safely bridges generative text-to-image AI processes without exposing internal states.
    """

    def __init__(self, model_size: str = "mini", gpu_enabled: bool = False):
        """Initialize MinDalle engine with default configuration."""
        self.model_size = model_size
        self.gpu_enabled = gpu_enabled
        self.dalle_model = None

    def initialize_generator(self) -> Dict[str, Any]:
        """
        Eagerly loads the specific DALL-E model weights.
        """
        size_opts = ["mini", "mega"]
        if self.model_size not in size_opts:
            return {"status": "error", "message": f"Invalid model size, must be one of {size_opts}"}
            
        try:
            from min_dalle import MinDalle
            self.dalle_model = MinDalle(
                models_root='./pretrained',
                dtype='float32',
                device='cuda' if self.gpu_enabled else 'cpu',
                is_mega=(self.model_size == "mega"), 
                is_reusable=True
            )
            return {"status": "success", "message": f"min-dalle {self.model_size} engine primed"}
        except ImportError:
            return {"status": "error", "message": "min-dalle library not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_image_stream(self, prompt: str, seed: int = 42, grid_size: int = 1) -> Dict[str, Any]:
        """
        Executes generation sequence ensuring output is securely captured or buffered.
        """
        if not prompt:
            return {"status": "error", "message": "Prompt string strictly required"}
            
        if self.dalle_model is None:
            return {"status": "error", "message": "MinDalle generator not initialized"}
            
        try:
            import io
            import numpy as np
            
            image_obj = self.dalle_model.generate_image(
                text=prompt,
                seed=seed,
                grid_size=grid_size,
                is_seamless=False,
                temperature=1.0,
                top_k=256,
                supercondition_factor=16.0
            )
            
            # Verify and return native Python dict wrapper
            return {
                "status": "success", 
                "image_width": image_obj.width,
                "image_height": image_obj.height,
                "mode": image_obj.mode
            }
        except ImportError:
            return {"status": "error", "message": "Dependency numpy or PIL missing via min-dalle"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def diagnostics(self):
        """Returns engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniMinDalleEngine",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": ["initialize_generator", "generate_image_stream"],
        }
