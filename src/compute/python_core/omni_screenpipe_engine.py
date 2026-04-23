"""OmniScreenpipeEngine.

Provides programmatic interaction with the Screenpipe service,
extracting multimodal desktop context (vision, audio).
"""
from typing import Dict, Any, List
import requests
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniScreenpipeEngine:
    """OMNI Engine for Screenpipe.
    
    Interfaces with the local Screenpipe daemon to retrieve
    captured screen and audio data for agentic context.
    """

    def __init__(self, endpoint: str = "http://localhost:3030"):
        """Initialize the Screenpipe API wrapper."""
        self.endpoint = endpoint

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniScreenpipeEngine",
            "status": "ready",
            "endpoint": self.endpoint
        }

    def search_context(self, query: str, limit: int = 10) -> Result[List[Dict[str, Any]], Exception]:
        """Searches recent desktop context using Screenpipe API.
        
        Args:
            query: Term to search in desktop text/OCR/audio transcripts.
            limit: Maximum number of results.
            
        Returns:
            Result wrapping list of context frames.
        """
        try:
            params = {"q": query, "limit": limit}
            resp = requests.get(f"{self.endpoint}/search", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Depending on Screenpipe API spec, data is usually enclosed in a 'data' array
            return Ok(data.get("data", []))
        except Exception as e:
            return Err(e)
