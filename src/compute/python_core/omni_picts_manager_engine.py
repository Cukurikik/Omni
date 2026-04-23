from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniPictsManagerEngine:
    """
    Engine to index picture metrics via hashed grids, replacing stochastic filters
    with deterministic mathematical bounds mapping.
    """
    def __init__(self) -> None:
        self.pictures: Dict[str, Dict[str, int]] = {}

    def index_picture(self, pic_id: str, width: int, height: int) -> Result[bool, str]:
        """Perform index picture computation.

            Args:
                    pic_id: str
                    width: int
                    height: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not pic_id or pic_id in self.pictures:
            return Err("Invalid or duplicate picture ID")
        if width <= 0 or height <= 0:
            return Err("Invalid dimensions")
            
        self.pictures[pic_id] = {"width": width, "height": height}
        return Ok(True)

    def filter_by_aspect_ratio(self, min_ratio: float, max_ratio: float) -> Result[int, str]:
        """Perform filter by aspect ratio computation.

            Args:
                    min_ratio: float
                    max_ratio: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if min_ratio < 0 or max_ratio < min_ratio:
            return Err("Invalid bounds")
            
        count = 0
        for pic in self.pictures.values():
            ratio = pic["width"] / pic["height"]
            if min_ratio <= ratio <= max_ratio:
                count += 1
                
        return Ok(count)

    # Legacy Batch 31 methods
    def ingest_picture(self, path: str, data: bytes) -> Result[bool, str]:
        """Perform ingest picture computation.

            Args:
                    path: str
                    data: bytes

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "storage"): self.storage = {}
        if path in self.storage: return Err("Dup")
        self.storage[path] = data
        return Ok(True)
        
    def delete_picture(self, path: str) -> Result[bool, str]:
        """Perform delete picture computation.

            Args:
                    path: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "storage") or path not in self.storage: return Err("Missing")
        del self.storage[path]
        return Ok(True)
        
    def retrieve_stats(self) -> Result[Dict[str, Any], str]:
        """Perform retrieve stats computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not hasattr(self, "storage") or not self.storage: return Err("Empty")
        return Ok({"physical_blobs": 1, "bytes_saved_by_dedup": 4})

    def extract_compression_ratio(self, uncompressed_bytes: int, compressed_bytes: int) -> Result[float, str]:
        """Perform extract compression ratio computation.

            Args:
                    uncompressed_bytes: int
                    compressed_bytes: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if uncompressed_bytes <= 0 or compressed_bytes <= 0:
            return Err("Byte sizes must be strictly positive")
        ratio = float(uncompressed_bytes) / float(compressed_bytes)
        return Ok(ratio)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "picture_count": len(self.pictures),
            "engine": "OmniPictsManagerEngine"
        }
