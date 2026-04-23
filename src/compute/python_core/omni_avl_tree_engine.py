"""OmniAvlTreeEngine for deterministic self-balancing tree logic."""
from typing import Dict, Any, List, Optional
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class AVLNode:
    def __init__(self, key: int):
        self.key = key
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height = 1

class OmniAvlTreeEngine(OmniBaseEngine):
    """Production-grade Omni Avl Tree Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def build_and_traverse(self, keys: List[int]) -> Result[Dict[str, Any], str]:
        """
        Builds an AVL tree and returns its in-order and pre-order traversal arrays, and tree depth.
        """
        try:
            root = None
            for key in keys:
                root = self._insert(root, key)

            in_order_res = []
            pre_order_res = []
            
            self._in_order(root, in_order_res)
            self._pre_order(root, pre_order_res)

            return Result.ok({
                "in_order": in_order_res,
                "pre_order": pre_order_res,
                "depth": self._get_height(root)
            })

        except Exception as e:
            return Result.fail(str(e))
            
    def _insert(self, node: Optional[AVLNode], key: int) -> AVLNode:
        if not node:
            return AVLNode(key)
        elif key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node # No duplicates

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        
        balance = self._get_balance(node)

        # Let Left Case
        if balance > 1 and key < node.left.key:
            return self._right_rotate(node)
        
        # Right Right Case
        if balance < -1 and key > node.right.key:
            return self._left_rotate(node)

        # Left Right Case
        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
            
        # Right Left Case
        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _left_rotate(self, z: AVLNode) -> AVLNode:
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _right_rotate(self, z: AVLNode) -> AVLNode:
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _get_height(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return node.height

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _in_order(self, node: Optional[AVLNode], res: List[int]):
        if node:
            self._in_order(node.left, res)
            res.append(node.key)
            self._in_order(node.right, res)

    def _pre_order(self, node: Optional[AVLNode], res: List[int]):
        if node:
            res.append(node.key)
            self._pre_order(node.left, res)
            self._pre_order(node.right, res)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniAvlTreeEngine",
            "status": "operational",
            "complexity": "O(N log N)"
        }
