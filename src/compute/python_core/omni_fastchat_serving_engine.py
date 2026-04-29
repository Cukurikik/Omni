"""
OMNI FastChat Serving Engine
Implementation of consistent hashing ring for token routing.
"""
import hashlib
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniFastChatServingEngine(OmniBaseEngine):
    def __init__(self, replicas: int = 3):
        super().__init__()
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

    def load_workers(self, workers: List[str]) -> Result[bool, str]:
        if not workers:
            return Err("Worker list is empty.")
        try:
            self.ring.clear()
            for worker in workers:
                for i in range(self.replicas):
                    key = self._hash(f"{worker}:{i}")
                    self.ring[key] = worker
            self.sorted_keys = sorted(self.ring.keys())
            return Ok(True)
        except Exception as e:
            return Err(f"Hash ring initiation failed: {str(e)}")

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def process(self, request_id: str) -> Result[str, str]:
        if not self.ring:
            return Err("Ring is empty, no workers loaded.")
        if not request_id:
            return Err("Invalid request ID.")
            
        try:
            h = self._hash(request_id)
            for key in self.sorted_keys:
                if h <= key:
                    return Ok(self.ring[key])
            return Ok(self.ring[self.sorted_keys[0]])
        except Exception as e:
            return Err(f"Token routing failed: {str(e)}")

    def diagnostics(self) -> Result[Dict[str, Any], str]:
        workers = ["worker-1", "worker-2", "worker-3"]
        self.load_workers(workers)
        res = self.process("test-req")
        if hasattr(res, 'is_ok') and res.is_ok() and res.unwrap() in workers:
            return Ok({"status": "healthy", "ring_size": len(self.ring)})
        return Err("Diagnostics failed on FastChat engine.")
