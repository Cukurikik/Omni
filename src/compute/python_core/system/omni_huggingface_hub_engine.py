import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OmniHuggingFaceHubEngine:
    """
    OMNI Engine for HuggingFace Hub Library.
    Manages repository interactions, model downloads, and safe cache allocation natively.
    """

    def __init__(self, cache_dir: str):
        """Initialize HuggingFaceHub engine with default configuration."""
        self.cache_dir = cache_dir
        self.authenticated = False

    def authenticate_hub(self, api_token: str) -> Dict[str, Any]:
        """
        Authenticates the OMNI pipeline with the HuggingFace Hub using a secure token.
        """
        if not api_token:
            return {"status": "error", "message": "API token cannot be empty"}
            
        try:
            import huggingface_hub
            huggingface_hub.login(token=api_token, add_to_git_credential=False)
            self.authenticated = True
            return {"status": "success", "message": "HuggingFace Hub authenticated"}
        except ImportError:
            return {"status": "error", "message": "huggingface_hub package not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fetch_model_info(self, repo_id: str) -> Dict[str, Any]:
        """
        Retrieves metadata and architecture info natively from a HF model repository.
        """
        if not repo_id:
            return {"status": "error", "message": "Repository ID must be provided"}
            
        try:
            import huggingface_hub
            model_info = huggingface_hub.model_info(repo_id=repo_id)
            return {"status": "success", "model_id": model_info.modelId, "pipeline_tag": model_info.pipeline_tag}
        except ImportError:
            return {"status": "error", "message": "huggingface_hub package not installed"}
        except huggingface_hub.utils.RepositoryNotFoundError:
            return {"status": "error", "message": f"Repository {repo_id} not found on Hub"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ensure_local_cache(self) -> Dict[str, Any]:
        """
        Secures the cache directory for incoming model binaries.
        """
        try:
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)
            return {"status": "success", "cache_ready": True}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        """Returns engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniHuggingFaceHubEngine",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": ["authenticate_hub", "fetch_model_info", "ensure_local_cache"],
            "cache_dir": self.cache_dir,
            "authenticated": self.authenticated,
        }
