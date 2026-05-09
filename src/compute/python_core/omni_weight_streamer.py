"""OMNI Compute — Weight Streaming Loader for Large Models"""
import os, logging, mmap, struct; from dataclasses import dataclass; from typing import Dict, Optional, BinaryIO
logger = logging.getLogger("omni.weight_stream")
@dataclass
class StreamConfig:
    chunk_size_mb: int = 64; use_mmap: bool = True; prefetch: bool = True
class WeightStreamer:
    """Stream model weights from disk without loading entirely into memory."""
    def __init__(self, c: StreamConfig): self.config = c; self.loaded_layers: Dict[str, bool] = {}
    def open_model(self, path: str) -> Dict:
        size = os.path.getsize(path)
        return {"path": path, "size_mb": size / (1024**2), "chunks": size // (self.config.chunk_size_mb * 1024 * 1024) + 1}
    def stream_layer(self, path: str, offset: int, size: int) -> bytes:
        with open(path, "rb") as f:
            if self.config.use_mmap:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                data = mm[offset:offset+size]; mm.close(); return data
            else:
                f.seek(offset); return f.read(size)
    def estimate_memory(self, model_size_gb: float, num_layers: int) -> Dict:
        per_layer = model_size_gb / num_layers
        streaming = per_layer * 2 + self.config.chunk_size_mb / 1024  # 2 layers + buffer
        return {"full_load_gb": model_size_gb, "streaming_gb": round(streaming, 2),
                "savings": f"{(1-streaming/model_size_gb)*100:.0f}%"}
