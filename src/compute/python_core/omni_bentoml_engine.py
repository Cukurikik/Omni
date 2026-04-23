"""OmniBentomlEngine.

Wrapper for bentoml/BentoML.
Orchestrates AI application serving and model inference pipelines.
"""
from typing import Dict, Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniBentomlEngine:
    """OMNI Engine for BentoML serving."""

    def __init__(self, bento_tag: str = "omni_model:latest"):
        """Initialize the BentoML inference pipeline."""
        self.bento_tag = bento_tag

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniBentomlEngine",
            "status": "ready",
            "bento_tag": self.bento_tag
        }

    def export_model_to_bento(self, model_obj: Any, name: str) -> Result[str, Exception]:
        """Saves a generic model to BentoML local model store.
        
        Args:
            model_obj: The pretrained machine learning model.
            name: The internal tracking name for Bento.
            
        Returns:
            Result wrapping the fully qualified BentoML tag string.
        """
        try:
            import bentoml
            # Using generic bentoml pickler as placeholder for polymorphic export
            saved_model = bentoml.picklable_model.save_model(name, model_obj)
            return Ok(str(saved_model.tag))
        except ImportError:
            return Err(Exception("bentoml is not installed."))
        except Exception as e:
            return Err(e)
