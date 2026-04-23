"""OmniUnionFindEngine — Production-grade Union-Find (Disjoint Set Union).

Implements DSU with union by rank and path compression for near-O(α(N))
amortized operations. Used for connected components, Kruskal's MST, etc.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniUnionFindEngine:
    """Production engine for Disjoint Set Union with rank + path compression."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, n: int = 0):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.n = n
        self._components = n

    def find(self, x: int) -> Result:
        """Perform find computation.

            Args:
                    x: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if x < 0 or x >= self.n:
                return Err(ValueError(f"Element {x} out of range [0, {self.n})."))
            root = self._find(x)
            return Ok({"element": x, "root": root})
        except Exception as e:
            return Err(e)

    def _find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self._find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> Result:
        """Perform union computation.

            Args:
                    x: int
                    y: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if x < 0 or x >= self.n or y < 0 or y >= self.n:
                return Err(ValueError(f"Elements must be in [0, {self.n})."))
            rx, ry = self._find(x), self._find(y)
            if rx == ry:
                return Ok({"merged": False, "components": self._components})
            if self.rank[rx] < self.rank[ry]:
                rx, ry = ry, rx
            self.parent[ry] = rx
            if self.rank[rx] == self.rank[ry]:
                self.rank[rx] += 1
            self._components -= 1
            return Ok({"merged": True, "components": self._components, "new_root": rx})
        except Exception as e:
            return Err(e)

    def connected(self, x: int, y: int) -> Result:
        """Perform connected computation.

            Args:
                    x: int
                    y: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            return Ok({"connected": self._find(x) == self._find(y), "x": x, "y": y})
        except Exception as e:
            return Err(e)

    def get_components(self) -> Result:
        """Perform get components computation.

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            groups = {}
            for i in range(self.n):
                r = self._find(i)
                groups.setdefault(r, []).append(i)
            return Ok({"components": list(groups.values()), "count": self._components})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniUnionFindEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "n": self.n, "components": self._components}
