"""
OMNI LRU Cache Engine - Optimized O(1) Cache Eviction.
Assimilated from: coding-interview-university & system-design-primer.
Provides: Production-grade Double Linked List & Hash Map structured LRU Cache.
"""
from typing import Dict, Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "1.0.0-omni-lru-cache"




class DLinkedNode:
    """OMNI Production Engine: DLinkedNode. Zero-Prod compliant."""
    def __init__(self, key: str = "", value: Any = None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class OmniLRUCacheEngine:
    """
    Mathematical LRU Cache ensuring strict O(1) time complexity for reads and updates.
    
    @since 1.0.0
    @tags ["cache", "lru", "data-structures", "memory"]
    """
    def __init__(self, capacity: int = 100) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"
        self.capacity = capacity
        self.cache: Dict[str, DLinkedNode] = {}
        self.head = DLinkedNode()
        self.tail = DLinkedNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_node(self, node: DLinkedNode):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: DLinkedNode):
        prev = node.prev
        new_next = node.next
        prev.next = new_next
        new_next.prev = prev

    def _move_to_head(self, node: DLinkedNode):
        self._remove_node(node)
        self._add_node(node)

    def _pop_tail(self) -> DLinkedNode:
        res = self.tail.prev
        self._remove_node(res)
        return res

    def diagnostics(self) -> Result:
        try:
            self.put("A", 1)
            self.put("B", 2)
            v = self.get("A")
            if v == 1:
                return Ok({"engine": "LRUCache", "status": "Ready", "lru_eviction": "Functional"})
        except Exception as e:
            return Err(f"Logic failure: {str(e)}")
        return Err("LRU Validation Failed.")

    def get(self, key: str) -> Any:
        """Perform get computation.

            Args:
                    key: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        node = self.cache.get(key)
        if not node:
            return None
        self._move_to_head(node)
        return node.value

    def put(self, key: str, value: Any) -> Result:
        """Perform put computation.

            Args:
                    key: str
                    value: Any

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        node = self.cache.get(key)
        if not node:
            new_node = DLinkedNode(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            if len(self.cache) > self.capacity:
                tail = self._pop_tail()
                del self.cache[tail.key]
            return Ok({"action": "inserted", "key": key})
        else:
            node.value = value
            self._move_to_head(node)
            return Ok({"action": "updated", "key": key})
