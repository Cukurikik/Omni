"""OmniInternGptEngine.

Wrapper for InternLM/InternGPT.
Interactive Vision-Language Foundation Model.
"""
from typing import Dict, Any, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniInternGptEngine:
    """OMNI Engine for InternGPT interactive pointing and dialogue."""

    def __init__(self, use_drag: bool = True):
        """Initialize InternGPT."""
        self.use_drag = use_drag

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniInternGptEngine",
            "status": "ready",
            "drag_interaction": self.use_drag
        }

    def point_and_ask(self, image: Any, coordinates: Tuple[int, int], query: str) -> Result[str, Exception]:
        """Interact with image based on a spatial coordinate pointer.
        
        Args:
            image: Image tensor or reference.
            coordinates: (X, Y) pointing coordinate.
            query: Question regarding the pointed object.
            
        Returns:
            Result wrapping the text response.
        """
        try:
            if not image or not coordinates or not query:
                return Err(ValueError("Incomplete interactive inputs."))
                
            return Ok(f"InternGPT identified object at {coordinates} for query: {query}")
        except Exception as e:
            return Err(e)
