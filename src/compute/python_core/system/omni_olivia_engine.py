import os
import json
from typing import Dict, Any
import subprocess

class OmniOliviaEngine:
    """
    OMNI Engine for Olivia AI chatbot.
    Interfaces with Olivia's Go-based backend or API.
    Source: https://github.com/olivia-ai/olivia.git
    """
    def __init__(self, workspace_dir: str = "", api_endpoint: str = "http://localhost:8080"):
        """Initialize Olivia engine with default configuration."""
        self.workspace_dir = workspace_dir or os.getcwd()
        self.api_endpoint = api_endpoint
        self._process = None

    def start_local_server(self) -> Dict[str, Any]:
        """Execute start local server operation for Olivia engine."""
        try:
            olivia_bin = os.path.join(self.workspace_dir, "olivia")
            if os.path.exists(olivia_bin):
                self._process = subprocess.Popen([olivia_bin])
                return {"status": "success", "message": "Olivia local server started."}
            return {"status": "error", "message": "Olivia binary not found in workspace."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_chat_request(self, text: str) -> Dict[str, Any]:
        """Formats the payload for Olivia API."""
        payload = {"sentence": text}
        return {"status": "success", "endpoint": f"{self.api_endpoint}/api/message", "payload": payload}

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniOliviaEngine",
            "endpoint": self.api_endpoint,
            "server_running": self._process is not None
        }
