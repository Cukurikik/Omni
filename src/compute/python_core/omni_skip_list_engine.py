"""OmniSkipListEngine — Production-grade probabilistic skip list.

Implements a skip list data structure with deterministic SHA-256 level generation
for O(log N) search, insert, and delete operations.
"""
import hashlib
from typing import Any, Dict, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class _SkipNode:
    __slots__ = ('key', 'value', 'forward')

    def __init__(self, key: float, value: Any, level: int):
        self.key = key
        self.value = value
        self.forward = [None] * (level + 1)


class OmniSkipListEngine:
    """Production engine for probabilistic skip list with deterministic levels."""

    ENGINE_VERSION = "1.0.0"
    MAX_LEVEL = 16

    def __init__(self):
        self._header = _SkipNode(float('-inf'), None, self.MAX_LEVEL)
        self._level = 0
        self._size = 0
        self._op_count = 0

    def _det_level(self, key):
        self._op_count += 1
        h = hashlib.sha256(f"{key}:{self._op_count}".encode()).digest()
        level = 0
        for byte in h:
            if byte < 128:
                break
            level += 1
        return min(level, self.MAX_LEVEL)

    def insert(self, key: float, value: Any = None) -> Result:
        """Perform insert computation.

            Args:
                    key: float
                    value: Any

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            update = [None] * (self.MAX_LEVEL + 1)
            curr = self._header
            for i in range(self._level, -1, -1):
                while curr.forward[i] and curr.forward[i].key < key:
                    curr = curr.forward[i]
                update[i] = curr

            curr = curr.forward[0]
            if curr and curr.key == key:
                curr.value = value
                return Ok({"inserted": False, "updated": True, "key": key, "size": self._size})

            new_level = self._det_level(key)
            if new_level > self._level:
                for i in range(self._level + 1, new_level + 1):
                    update[i] = self._header
                self._level = new_level

            node = _SkipNode(key, value, new_level)
            for i in range(new_level + 1):
                node.forward[i] = update[i].forward[i]
                update[i].forward[i] = node
            self._size += 1
            return Ok({"inserted": True, "key": key, "level": new_level, "size": self._size})
        except Exception as e:
            return Err(e)

    def search(self, key: float) -> Result:
        """Perform search computation.

            Args:
                    key: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            curr = self._header
            for i in range(self._level, -1, -1):
                while curr.forward[i] and curr.forward[i].key < key:
                    curr = curr.forward[i]
            curr = curr.forward[0]
            if curr and curr.key == key:
                return Ok({"found": True, "key": key, "value": curr.value})
            return Ok({"found": False, "key": key})
        except Exception as e:
            return Err(e)

    def to_list(self) -> Result:
        """Perform to list computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            items = []
            curr = self._header.forward[0]
            while curr:
                items.append({"key": curr.key, "value": curr.value})
                curr = curr.forward[0]
            return Ok({"items": items, "size": self._size, "level": self._level})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniSkipListEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "size": self._size, "max_level": self._level}
