"""OmniConsistentHashingEngine — Production-grade consistent hashing ring.

Implements consistent hashing with virtual nodes for load balancing,
SHA-256 based hash function, and O(log N) key lookup via binary search.
"""
import hashlib
import bisect
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniConsistentHashingEngine:
    """Production engine for consistent hashing ring."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, replicas: int = 150):
        self.replicas = replicas
        self._ring: List[int] = []
        self._node_map: Dict[int, str] = {}
        self._nodes: set = set()

    @staticmethod
    def _hash(key: str) -> int:
        return int(hashlib.sha256(key.encode()).hexdigest()[:16], 16)

    def add_node(self, node: str) -> Result:
        """Add a node to the consistent hashing ring with virtual replicas."""
        try:
            if node in self._nodes:
                return Err(ValueError(f"Node '{node}' already in ring."))
            self._nodes.add(node)
            for i in range(self.replicas):
                vh = self._hash(f"{node}:{i}")
                self._ring.append(vh)
                self._node_map[vh] = node
            self._ring.sort()
            return Ok({"node": node, "virtual_nodes_added": self.replicas, "ring_size": len(self._ring)})
        except Exception as e:
            return Err(e)

    def remove_node(self, node: str) -> Result:
        """Remove a node and its virtual replicas from the ring."""
        try:
            if node not in self._nodes:
                return Err(ValueError(f"Node '{node}' not in ring."))
            self._nodes.discard(node)
            for i in range(self.replicas):
                vh = self._hash(f"{node}:{i}")
                self._ring.remove(vh)
                del self._node_map[vh]
            return Ok({"node": node, "removed": True, "ring_size": len(self._ring)})
        except Exception as e:
            return Err(e)

    def get_node(self, key: str) -> Result:
        """Look up which node a given key maps to. O(log N) via binary search."""
        try:
            if not self._ring:
                return Err(ValueError("Ring is empty; add nodes first."))
            h = self._hash(key)
            idx = bisect.bisect_right(self._ring, h)
            if idx == len(self._ring):
                idx = 0
            ring_hash = self._ring[idx]
            node = self._node_map[ring_hash]
            return Ok({"key": key, "node": node, "key_hash": h, "ring_position": idx})
        except Exception as e:
            return Err(e)

    def get_distribution(self, keys: List[str]) -> Result:
        """Compute key distribution across nodes."""
        try:
            dist: Dict[str, int] = {n: 0 for n in self._nodes}
            for key in keys:
                res = self.get_node(key)
                if res.is_ok():
                    dist[res.value["node"]] += 1
            total = len(keys)
            balance = {n: round(c / total, 6) if total > 0 else 0.0 for n, c in dist.items()}
            return Ok({"distribution": dist, "balance_ratio": balance, "total_keys": total,
                        "nodes": len(self._nodes)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniConsistentHashingEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "nodes": len(self._nodes), "ring_size": len(self._ring)}
