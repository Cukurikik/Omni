"""OmniDeeplakeEngine.

Wrapper for activeloopai/deeplake.
AI Data Runtime providing serverless vector store and datalake.
"""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniDeeplakeEngine:
    """OMNI Engine for activeloop deeplake."""

    def __init__(self, dataset_path: str = "./omni_datalake"):
        """Initialize the Deeplake dataset runtime."""
        self.dataset_path = dataset_path
        self._ds = None

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniDeeplakeEngine",
            "status": "connected" if self._ds else "uninitialized",
            "dataset_path": self.dataset_path
        }

    def store_tensors(self, tensor_name: str, data: List[Any]) -> Result[int, Exception]:
        """Stores a batch of tensors to the datalake.
        
        Args:
            tensor_name: The name of the tensor group.
            data: List of data arrays or objects.
            
        Returns:
            Result wrapping the number of records appended.
        """
        try:
            import deeplake
            if self._ds is None:
                self._ds = deeplake.dataset(self.dataset_path)
            
            if tensor_name not in self._ds.tensors:
                self._ds.create_tensor(tensor_name)
                
            self._ds[tensor_name].extend(data)
            return Ok(len(data))
        except ImportError:
            return Err(Exception("deeplake package is missing."))
        except Exception as e:
            return Err(e)
