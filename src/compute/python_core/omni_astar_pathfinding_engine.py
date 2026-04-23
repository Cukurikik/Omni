"""OmniAstarPathfindingEngine — Production-grade A* pathfinding on 2D grids.

Implements A* search with Manhattan and Euclidean heuristics, min-heap
priority queue, and path reconstruction for grid-based navigation.
"""
import heapq
import math
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniAstarPathfindingEngine:
    """Production engine for A* pathfinding on 2D obstacle grids."""

    ENGINE_VERSION = "1.0.0"
    DIRECTIONS_4 = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    DIRECTIONS_8 = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    @staticmethod
    def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _euclidean(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def find_path(self, grid: List[List[int]], start: Tuple[int, int], goal: Tuple[int, int],
                  heuristic: str = "manhattan", allow_diagonal: bool = False) -> Result:
        """
        Find shortest path on a 2D grid using A*.

        Args:
            grid: 2D list where 0=walkable, 1=obstacle.
            start: (row, col) start position.
            goal: (row, col) goal position.
            heuristic: "manhattan" or "euclidean".
            allow_diagonal: If True, allows 8-directional movement.

        Returns:
            Result with path, cost, and nodes explored count.
        """
        try:
            if not grid or not grid[0]:
                return Err(ValueError("Grid must be non-empty."))
            rows, cols = len(grid), len(grid[0])
            if not (0 <= start[0] < rows and 0 <= start[1] < cols):
                return Err(ValueError(f"Start {start} is out of bounds."))
            if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
                return Err(ValueError(f"Goal {goal} is out of bounds."))
            if grid[start[0]][start[1]] == 1:
                return Err(ValueError("Start position is an obstacle."))
            if grid[goal[0]][goal[1]] == 1:
                return Err(ValueError("Goal position is an obstacle."))

            h_fn = self._manhattan if heuristic == "manhattan" else self._euclidean
            dirs = self.DIRECTIONS_8 if allow_diagonal else self.DIRECTIONS_4

            open_set = [(h_fn(start, goal), 0.0, start)]
            came_from = {}
            g_score = {start: 0.0}
            explored = 0

            while open_set:
                f, g, current = heapq.heappop(open_set)
                explored += 1

                if current == goal:
                    path = []
                    c = current
                    while c in came_from:
                        path.append(list(c))
                        c = came_from[c]
                    path.append(list(start))
                    path.reverse()
                    return Ok({"path": path, "cost": round(g_score[goal], 6),
                               "path_length": len(path), "nodes_explored": explored,
                               "heuristic": heuristic, "diagonal": allow_diagonal})

                if g > g_score.get(current, math.inf):
                    continue

                for dr, dc in dirs:
                    nr, nc = current[0] + dr, current[1] + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                        neighbor = (nr, nc)
                        move_cost = math.sqrt(2) if (dr != 0 and dc != 0) else 1.0
                        ng = g + move_cost
                        if ng < g_score.get(neighbor, math.inf):
                            g_score[neighbor] = ng
                            came_from[neighbor] = current
                            heapq.heappush(open_set, (ng + h_fn(neighbor, goal), ng, neighbor))

            return Ok({"path": None, "cost": None, "path_length": 0,
                        "nodes_explored": explored, "reachable": False})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniAstarPathfindingEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(E log V) A* with admissible heuristic"}
