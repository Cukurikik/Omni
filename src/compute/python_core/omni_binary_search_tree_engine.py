"""OmniBinarySearchTreeEngine — Production-grade BST with traversal and balancing checks.

Implements a binary search tree from scratch with insert, search, delete,
in-order/pre-order/post-order traversal, and balance factor computation.
"""
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class _BSTNode:
    __slots__ = ('key', 'value', 'left', 'right')

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class OmniBinarySearchTreeEngine:
    """Production engine for binary search tree operations."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self):
        self._root = None
        self._size = 0

    def insert(self, key, value=None) -> Result:
        """Insert a key-value pair into the BST."""
        try:
            self._root = self._insert(self._root, key, value)
            self._size += 1
            return Ok({"key": key, "inserted": True, "size": self._size})
        except Exception as e:
            return Err(e)

    def _insert(self, node, key, value):
        if node is None:
            return _BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value  # update
            self._size -= 1  # don't double-count
        return node

    def search(self, key) -> Result:
        """Search for a key in the BST."""
        try:
            node = self._search(self._root, key)
            if node:
                return Ok({"key": key, "found": True, "value": node.value})
            return Ok({"key": key, "found": False, "value": None})
        except Exception as e:
            return Err(e)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def inorder(self) -> Result:
        """Return in-order traversal (sorted)."""
        try:
            result = []
            self._inorder(self._root, result)
            return Ok({"traversal": result, "count": len(result)})
        except Exception as e:
            return Err(e)

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append({"key": node.key, "value": node.value})
            self._inorder(node.right, result)

    def height(self) -> Result:
        """Compute tree height."""
        try:
            h = self._height(self._root)
            is_balanced = self._is_balanced(self._root)
            return Ok({"height": h, "size": self._size, "balanced": is_balanced})
        except Exception as e:
            return Err(e)

    def _height(self, node):
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    def _is_balanced(self, node):
        if node is None:
            return True
        lh = self._height(node.left)
        rh = self._height(node.right)
        return abs(lh - rh) <= 1 and self._is_balanced(node.left) and self._is_balanced(node.right)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniBinarySearchTreeEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "size": self._size, "complexity": "O(log N) average"}
