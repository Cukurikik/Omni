"""OmniQwenVlEngine.

Wrapper for QwenLM/Qwen-VL.
Large-scale vision-language model for multimodal understanding.
"""
from typing import Dict, Any, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniQwenVlEngine:
    """OMNI Engine for Qwen-VL."""

    def __init__(self, model_name: str = "Qwen/Qwen-VL-Chat"):
        """Initialize Qwen-VL multimodal model."""
        self.model_name = model_name
        self._tokenizer = None
        self._model = None

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniQwenVlEngine",
            "status": "ready" if self._model else "uninitialized",
            "model_name": self.model_name
        }

    def process_vision_query(self, image_path: str, query: str) -> Result[str, Exception]:
        """Processes an image query using Qwen-VL.
        
        Args:
            image_path: Path to the local image.
            query: Question regarding the image.
            
        Returns:
            Result wrapping the string response.
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            if self._model is None:
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                self._model = AutoModelForCausalLM.from_pretrained(self.model_name, device_map="auto", trust_remote_code=True).eval()

            # Qwen-VL specific prompt formatting
            query_str = f"<img>{image_path}</img>{query}"
            response, history = self._model.chat(self._tokenizer, query=query_str, history=None)
            
            return Ok(response)
        except ImportError:
            return Err(Exception("transformers package missing."))
        except Exception as e:
            return Err(e)
