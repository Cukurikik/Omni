import os
import json
from typing import Dict, Any, List

class OmniHuggingFaceNLPEngine:
    """
    OMNI Engine for HuggingFace Transformers (NLP).
    Handles pipelines for text classification, generation, etc.
    Source: https://github.com/huggingface/course.git
    """
    def __init__(self, workspace_dir: str = "", model_id: str = "bert-base-uncased"):
        """Initialize HuggingFaceNLP engine with default configuration."""
        self.workspace_dir = workspace_dir or os.getcwd()
        self.model_id = model_id
        self._cache_dir = os.path.join(self.workspace_dir, ".omni_hf_cache")
        os.makedirs(self._cache_dir, exist_ok=True)
        self._pipe = None

    def load_pipeline(self, task: str = "text-classification") -> Dict[str, Any]:
        """Loads a HuggingFace pipeline in a zero-mock but safe manner."""
        try:
            import transformers
            self._pipe = transformers.pipeline(task, model=self.model_id, model_kwargs={"cache_dir": self._cache_dir})
            return {"status": "success", "message": f"Pipeline {task} loaded with {self.model_id}"}
        except ImportError:
            return {"status": "error", "message": "transformers package not installed"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to load pipeline: {str(e)}"}

    def run_inference(self, text: str) -> Dict[str, Any]:
        """Runs pipeline inference on provided text."""
        if self._pipe is None:
            return {"status": "error", "message": "Pipeline not loaded. Call load_pipeline first."}
        try:
            result = self._pipe(text)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": f"Inference failed: {str(e)}"}

    def clear_cache(self) -> Dict[str, Any]:
        """Clears local HF cache folder to free memory/disk."""
        try:
            import shutil
            shutil.rmtree(self._cache_dir, ignore_errors=True)
            return {"status": "success", "message": "HF engine cache cleared."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniHuggingFaceNLPEngine",
            "model_id": self.model_id,
            "pipeline_loaded": self._pipe is not None,
            "cache_dir": self._cache_dir
        }
