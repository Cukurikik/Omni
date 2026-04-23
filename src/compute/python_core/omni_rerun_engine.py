"""OmniRerunEngine.

Wrapper for rerun-io/rerun multimodal data visualizer.
Provides programmatic logging of tensors, images, and point clouds.
"""
from typing import Dict, Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniRerunEngine:
    """OMNI Engine for rerun-io/rerun."""

    def __init__(self, application_id: str = "omni_framework"):
        """Initialize the Rerun multimodal logger engine."""
        self.application_id = application_id
        self._is_initialized = False

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniRerunEngine",
            "status": "initialized" if self._is_initialized else "ready",
            "application_id": self.application_id
        }

    def init_and_connect(self) -> Result[bool, Exception]:
        """Initializes Rerun and connects to the visualizer."""
        try:
            import rerun as rr
            rr.init(self.application_id, spawn=False)
            # Default TCP connection to local viewer
            rr.connect()
            self._is_initialized = True
            return Ok(True)
        except ImportError:
            return Err(Exception("rerun-sdk not installed."))
        except Exception as e:
            return Err(e)

    def log_image(self, entity_path: str, image_path: str) -> Result[bool, Exception]:
        """Logs an image to the Rerun viewer.
        
        Args:
            entity_path: The rerun entity path e.g. 'camera/image'
            image_path: Path to the image file to visually log.
            
        Returns:
            Result wrapping boolean True if successful.
        """
        try:
            import rerun as rr
            if not self._is_initialized:
                self.init_and_connect()
            
            rr.log(entity_path, rr.ImageEncoded(path=image_path))
            return Ok(True)
        except Exception as e:
            return Err(e)
