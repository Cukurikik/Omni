"""OmniJinaServeEngine.

Provides programmatic builder and dispatcher for Jina Flows,
enabling cloud-native multimodal AI applications.
"""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniJinaServeEngine:
    """OMNI Engine for Jina AI Serve."""

    def __init__(self, host: str = "0.0.0.0", port: int = 54321):
        """Initialize the Jina Serve orchestration engine."""
        self.host = host
        self.port = port
        self._client = None

    def diagnostics(self) -> Dict[str, Any]:
        """Returns engine diagnostic metadata."""
        return {
            "engine": "OmniJinaServeEngine",
            "status": "ready" if self._client else "uninitialized",
            "host": self.host,
            "port": self.port
        }

    def execute_flow_request(self, payload: Dict[str, Any]) -> Result[Dict[str, Any], Exception]:
        """Executes a multimodal request against a running Jina flow.
        
        Args:
            payload: Standard dictionary representing document tags or input.
            
        Returns:
            Result wrapping the response document tags from Jina framework.
        """
        try:
            from jina import Client, Document, DocumentArray
            if self._client is None:
                self._client = Client(host=f"grpc://{self.host}:{self.port}")
            
            docs = DocumentArray([Document(tags=payload)])
            response = self._client.post("/", docs)
            
            if len(response) > 0:
                tags = getattr(response[0], "tags", {})
                return Ok({"result": tags})
            return Ok({"result": {}})
        except ImportError:
            return Err(Exception("Jina AI library not installed. Please install 'jina' package."))
        except Exception as e:
            return Err(e)
