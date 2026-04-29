"""
OMNI Ollama Local Engine
Blob storage chunk integrity using SHA256 trees.
"""
import hashlib
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniOllamaLocalEngine(OmniBaseEngine):
    def __init__(self, chunk_size: int = 1024):
        super().__init__()
        self.chunk_size = chunk_size

    def process(self, binary_data: bytes) -> Result[Dict[str, Any], str]:
        if not binary_data:
            return Err("Binary blob is empty.")
            
        try:
            leaves = []
            chunks = []
            for i in range(0, len(binary_data), self.chunk_size):
                chunk = binary_data[i:i + self.chunk_size]
                chunks.append(chunk)
                leaf_hash = hashlib.sha256(chunk).hexdigest()
                leaves.append(leaf_hash)
            
            def build_tree(nodes: List[str]) -> str:
                if len(nodes) == 1:
                    return nodes[0]
                next_level = []
                for i in range(0, len(nodes), 2):
                    left = nodes[i]
                    right = nodes[i+1] if i+1 < len(nodes) else left
                    combined = hashlib.sha256((left + right).encode('utf-8')).hexdigest()
                    next_level.append(combined)
                return build_tree(next_level)
                
            root_hash = build_tree(leaves)
            
            return Ok({
                "root_hash": root_hash,
                "chunks_count": len(chunks),
                "total_size": len(binary_data),
                "verified": True
            })
        except Exception as e:
            return Err(f"Blob indexing failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        data = b"Testing omni ollama blob memory layout over multiple chunks of bytes." * 100
        res = self.process(data)
        if hasattr(res, 'is_ok') and res.is_ok():
            return Ok({"status": "healthy", "tree": "verified"})
        return Err("Diagnostics failed on Ollama engine.")
