import datetime
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniCellularAutomataEngine:
    """
    OmniCellularAutomataEngine
    Batch: 27 (Semester 10)
    
    A zero-mock generalized engine for evaluating complexity theory automata
    such as Conway's Game of Life on structured matrix intervals.
    """
    
    def __init__(self, rule_survive: List[int], rule_born: List[int], grid_dimensions: Tuple[int, int]):
        """
        :param rule_survive: Valid neighbor counts for an existing cell to survive (e.g. [2,3])
        :param rule_born: Valid neighbor counts for a dead cell to be born (e.g. [3])
        :param grid_dimensions: (rows, cols)
        """
        self.rule_survive = sorted(rule_survive)
        self.rule_born = sorted(rule_born)
        self.rows, self.cols = grid_dimensions

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "rule": f"B{''.join(map(str, self.rule_born))}/S{''.join(map(str, self.rule_survive))}",
            "grid": f"{self.rows}x{self.cols}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _validate_grid(self, grid: List[List[int]]) -> Result[bool, Exception]:
        """Ensures grid strictly matches the domain topology constraints."""
        if not isinstance(grid, list):
            return Err(TypeError("Grid must be a list of lists"))
        if len(grid) != self.rows:
            return Err(ValueError(f"Row count mismatch: expected {self.rows}, got {len(grid)}"))
            
        for r_idx, row in enumerate(grid):
            if not isinstance(row, list):
                return Err(TypeError(f"Row {r_idx} is not a list"))
            if len(row) != self.cols:
                return Err(ValueError(f"Col count mismatch row {r_idx}: expected {self.cols}, got {len(row)}"))
            for val in row:
                if val not in (0, 1):
                    return Err(ValueError(f"Invalid state {val} detected. Only 0/1 binary permitted."))
                    
        return Ok(True)

    def _count_neighbors(self, grid: List[List[int]], r: int, c: int) -> int:
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                # Toroidal wrap-around boundaries
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                count += grid[nr][nc]
        return count

    def compute_next_generation(self, current_grid: List[List[int]]) -> Result[List[List[int]], Exception]:
        """
        Forward mathematical step calculating the exact discrete timestamp boundary frame (T+1).
        """
        try:
            val_res = self._validate_grid(current_grid)
            if not val_res.is_ok():
                return Err(val_res.unwrap_err())
                
            next_grid = [[0 for _ in range(self.cols)] for __ in range(self.rows)]
            
            for r in range(self.rows):
                for c in range(self.cols):
                    neighbors = self._count_neighbors(current_grid, r, c)
                    state = current_grid[r][c]
                    
                    if state == 1:
                        if neighbors in self.rule_survive:
                            next_grid[r][c] = 1
                        else:
                            next_grid[r][c] = 0
                    else:
                        if neighbors in self.rule_born:
                            next_grid[r][c] = 1
                        else:
                            next_grid[r][c] = 0
                            
            return Ok(next_grid)
            
        except Exception as e:
            return Err(e)
