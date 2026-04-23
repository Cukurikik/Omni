"""OmniBTreeEngine for B-Tree operations."""
from typing import Dict, Any, List, Optional
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class _BTreeNode:
    def __init__(self, leaf: bool = False):
        self.keys = []
        self.children = []
        self.leaf = leaf

class OmniBTreeEngine(OmniBaseEngine):
    """Production-grade Omni B Tree Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self, t: int = 3):
        self.root = _BTreeNode(leaf=True)
        self.t = t

    def insert(self, k: int) -> Result[Dict[str, Any], str]:
        """Inserts a key into the B-Tree."""
        try:
            root = self.root
            if len(root.keys) == (2 * self.t) - 1:
                new_node = _BTreeNode()
                self.root = new_node
                new_node.children.append(root)
                self._split_child(new_node, 0)
                self._insert_non_full(new_node, k)
            else:
                self._insert_non_full(root, k)
            return Result.ok({"inserted": k})
        except Exception as e:
            return Result.fail(str(e))

    def _split_child(self, x: _BTreeNode, i: int):
        t = self.t
        y = x.children[i]
        z = _BTreeNode(leaf=y.leaf)
        x.children.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t: (2 * t - 1)]
        y.keys = y.keys[0: t - 1]
        if not y.leaf:
            z.children = y.children[t: 2 * t]
            y.children = y.children[0: t]

    def _insert_non_full(self, x: _BTreeNode, k: int):
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(0)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.children[i], k)

    def search(self, k: int) -> Result[Dict[str, Any], str]:
        """Searches for a key."""
        try:
            found = self._search_node(self.root, k)
            return Result.ok({"found": found})
        except Exception as e:
            return Result.fail(str(e))

    def _search_node(self, x: _BTreeNode, k: int) -> bool:
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return True
        elif x.leaf:
            return False
        else:
            return self._search_node(x.children[i], k)

    def in_order(self) -> Result[Dict[str, Any], str]:
        """Perform in order computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            keys = []
            self._in_order_node(self.root, keys)
            return Result.ok({"keys": keys})
        except Exception as e:
            return Result.fail(str(e))

    def _in_order_node(self, x: _BTreeNode, res: List[int]):
        for i in range(len(x.keys)):
            if not x.leaf:
                self._in_order_node(x.children[i], res)
            res.append(x.keys[i])
        if not x.leaf:
            self._in_order_node(x.children[len(x.keys)], res)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniBTreeEngine",
            "status": "operational",
            "t": self.t
        }
