"""OmniAnythingLlmEngine.

Provides production wrapper to interact with AnythingLLM API endpoints
for workspace orchestration and multi-document chat interaction.
"""
from typing import Dict, Any
import requests
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniAnythingLlmEngine:
    """OMNI Engine for Mintplex-Labs AnythingLLM."""

    def __init__(self, base_url: str = "http://localhost:3001/api", api_key: str = ""):
        """Initialize the AnythingLLM engine API connector."""
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def diagnostics(self) -> Dict[str, Any]:
        """Returns engine diagnostic metadata."""
        return {
            "engine": "OmniAnythingLlmEngine",
            "status": "ready",
            "base_url": self.base_url
        }

    def create_workspace(self, name: str) -> Result[Dict[str, Any], Exception]:
        """Creates a new workspace in AnythingLLM.
        
        Args:
            name: The human readable name of the workspace.
            
        Returns:
            Result wrapping the response dictionary on success.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/workspace/new",
                json={"name": name},
                headers=self.headers,
                timeout=10
            )
            resp.raise_for_status()
            return Ok(resp.json())
        except Exception as e:
            return Err(e)

    def chat_workspace(self, workspace_slug: str, message: str) -> Result[Dict[str, Any], Exception]:
        """Chats with a specific workspace context.
        
        Args:
            workspace_slug: The identifier slug of the workspace.
            message: The textual prompt to send.
            
        Returns:
            Result wrapping the LLM response.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/workspace/{workspace_slug}/chat",
                json={"message": message, "mode": "chat"},
                headers=self.headers,
                timeout=30
            )
            resp.raise_for_status()
            return Ok(resp.json())
        except Exception as e:
            return Err(e)
