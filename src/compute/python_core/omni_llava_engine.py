"""OmniLlavaEngine.

Provides multimodal inference orchestration.
Connects with Visual Instruction Tuning capability.
"""
from typing import Dict, Any, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniLlavaEngine:
    """OMNI Engine for haotian-liu/LLaVA."""

    def __init__(self, model_id: str = "llava-hf/llava-1.5-7b-hf"):
        """Initialize the LLaVA vision-language inference engine."""
        self.model_id = model_id
        self._model = None

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniLlavaEngine",
            "status": "ready" if self._model else "uninitialized",
            "model_id": self.model_id
        }

    def process_image_query(self, image_path: str, prompt: str) -> Result[str, Exception]:
        """Processes an image query using the LLaVA model.
        
        Args:
            image_path: Path to the image file.
            prompt: Visual instruction prompt to execute.
            
        Returns:
            Result wrapping the text generation output.
        """
        try:
            from PIL import Image
            from transformers import pipeline
            if self._model is None:
                self._model = pipeline("image-to-text", model=self.model_id)
            
            image = Image.open(image_path)
            # Standard llava prompt format usually handled by pipeline
            out = self._model(image, prompt=prompt)
            if out and isinstance(out, list) and len(out) > 0:
                text = out[0].get("generated_text", "")
                return Ok(text)
            return Ok("")
        except ImportError:
            return Err(Exception("Transformers and PIL required: 'pip install transformers Pillow'"))
        except Exception as e:
            return Err(e)
