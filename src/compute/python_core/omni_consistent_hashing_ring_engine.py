import datetime
import hashlib
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniConsistentHashingRingEngine:
    """
    OmniConsistentHashingRingEngine
    Batch: 29 (Semester 10)
    
    A zero-mock distributed systems topology engine execute a
    mathematical consistent hash ring boundary map with virtual nodes.
    """
    
    def __init__(self, virtual_nodes: int = 100):
        """
        :param virtual_nodes: The number of virtual points per physical node
        """
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.nodes: set = set()

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "virtual_nodes": self.virtual_nodes,
            "total_ring_size": len(self.ring),
            "physical_nodes": len(self.nodes),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _hash(self, key: str) -> int:
        """Deterministic integer conversion of string scalar value using MD5."""
        m = hashlib.md5()
        m.update(key.encode('utf-8'))
        # Return standard 32-bit bound
        return int(m.hexdigest(), 16) & 0xFFFFFFFF

    def add_node(self, node_id: str) -> Result[bool, Exception]:
        """
        Injects a logical distributed node cluster unit into the ring map.
        """
        try:
            if not isinstance(node_id, str):
                return Err(TypeError("Node ID must be a string"))
                
            if node_id in self.nodes:
                return Ok(False) # Already exists
                
            self.nodes.add(node_id)
            for i in range(self.virtual_nodes):
                v_key = f"{node_id}#v{i}"
                h = self._hash(v_key)
                self.ring[h] = node_id
                self.sorted_keys.append(h)
                
            self.sorted_keys.sort()
            return Ok(True)
        except Exception as e:
            return Err(e)

    def remove_node(self, node_id: str) -> Result[bool, Exception]:
        """
        Eradicates a distributed topology point and reconstructs continuous boundaries.
        """
        try:
            if not isinstance(node_id, str):
                return Err(TypeError("Node ID must be a string"))
                
            if node_id not in self.nodes:
                return Ok(False) # Didn't exist
                
            self.nodes.remove(node_id)
            for i in range(self.virtual_nodes):
                v_key = f"{node_id}#v{i}"
                h = self._hash(v_key)
                if h in self.ring:
                    del self.ring[h]
                if h in self.sorted_keys:
                    self.sorted_keys.remove(h)
                    
            return Ok(True)
        except Exception as e:
            return Err(e)

    def locate_node(self, payload_key: str) -> Result[str, Exception]:
        """
        Computes absolute distributed target mapping assignment based on continuous wrap limits.
        """
        try:
            if not self.ring:
                return Err(RuntimeError("Ring is empty, cannot compute target bounds."))
                
            if not isinstance(payload_key, str):
                return Err(TypeError("Payload key must be a string"))
                
            h = self._hash(payload_key)
            
            # Binary search boundary (right-bisect equivalent)
            low, high = 0, len(self.sorted_keys) - 1
            idx = 0
            
            if h > self.sorted_keys[-1]:
                idx = 0 # wrap around boundary
            else:
                while low <= high:
                    mid = (low + high) // 2
                    if self.sorted_keys[mid] < h:
                        low = mid + 1
                    else:
                        idx = mid
                        high = mid - 1
                        
            target_hash = self.sorted_keys[idx]
            return Ok(self.ring[target_hash])
            
        except Exception as e:
            return Err(e)
