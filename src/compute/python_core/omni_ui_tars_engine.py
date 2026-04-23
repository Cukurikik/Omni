"""OmniUITarsEngine.

Acts as the main orchestration bridge to send GUI automation
prompts to the UI-TARS agent system for desktop control.
"""
from typing import Dict, Any
import requests
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniUITarsEngine:
    """OMNI Engine for ByteDance UI-TARS-desktop."""

    def __init__(self, endpoint: str = "http://localhost:8080/v1/execute"):
        """Initialize the UI TARS engine connector."""
        self.endpoint = endpoint

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniUITarsEngine",
            "status": "ready",
            "endpoint": self.endpoint
        }

    def execute_command(self, instruction: str) -> Result[Dict[str, Any], Exception]:
        """Sends an autonomous GUI macro command to the TARS backend.
        
        Args:
            instruction: Natural language instruction for the UI agent.
            
        Returns:
            Result wrapping execution metadata and status.
        """
        try:
            payload = {"instruction": instruction}
            resp = requests.post(self.endpoint, json=payload, timeout=60)
            resp.raise_for_status()
            return Ok(resp.json())
        except Exception as e:
            return Err(e)
