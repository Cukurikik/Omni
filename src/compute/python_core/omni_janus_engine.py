"""OmniJanusEngine.

Orchestrates DeepSeek Janus models for any-to-any multimodal
generation and understanding.
"""
from typing import Dict, Any, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniJanusEngine:
    """OMNI Engine for deepseek-ai/Janus.
    
    Provides multimodal inference using unified understanding models.
    """

    def __init__(self, model_name: str = "deepseek-ai/Janus-Pro-7B"):
        """Initialize the DeepSeek Janus model engine."""
        self.model_name = model_name
        self._processor = None
        self._model = None

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniJanusEngine",
            "status": "ready" if self._model else "uninitialized",
            "model_name": self.model_name
        }

    def process_multimodal_prompt(self, image_path: Optional[str], prompt: str) -> Result[str, Exception]:
        """Processes an image and text prompt using Janus.
        
        Args:
            image_path: Path to the image file, or None if purely text.
            prompt: The text prompt.
            
        Returns:
            Result wrapping the generated text string.
        """
        try:
            import torch
            from PIL import Image
            from transformers import AutoProcessor, AutoModelForCausalLM
            
            if self._model is None:
                self._processor = AutoProcessor.from_pretrained(self.model_name, trust_remote_code=True)
                self._model = AutoModelForCausalLM.from_pretrained(self.model_name, trust_remote_code=True)
                
            messages = [{"role": "user", "content": prompt}]
            if image_path:
                image = Image.open(image_path)
                inputs = self._processor(images=[image], text=prompt, return_tensors="pt")
            else:
                inputs = self._processor(text=prompt, return_tensors="pt")
                
            out = self._model.generate(**inputs, max_new_tokens=512)
            decoded = self._processor.decode(out[0], skip_special_tokens=True)
            return Ok(decoded)
        except ImportError:
            return Err(Exception("Transformers and torch required for Janus."))
        except Exception as e:
            return Err(e)
