"""
OMNI AlgoWiki Engine
====================
Production-grade abstraction inspired by vicky002/AlgoWiki.
Implements optimized mathematical graph traversal algorithms (Dijkstra)
via structural dense matrices directly in Numpy to avoid loop iterations where possible.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class AlgoWikiError(Exception):
    """Base error for Algorithm abstractions."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. ALGORITHMIC GRAPH RESOLVER (DIJKSTRA ITERATION)
# ---------------------------------------------------------------------------

class GraphResolver:
    """Numpy-native adjacency matrix parsing for shortest subset extraction."""
    
    def __init__(self, node_count: int):
        """Initialize GraphResolver."""
        self.nodes = node_count
        # Initialize dense adjacency matrix with infinity (no connections)
        self.adj_matrix = np.full((self.nodes, self.nodes), np.inf, dtype=np.float64)
        np.fill_diagonal(self.adj_matrix, 0.0) # distance to self is 0
        
    def add_edge(self, source: int, target: int, weight: float, directed: bool = False) -> Result:
        """Add edge to GraphResolver."""
        if source < 0 or source >= self.nodes or target < 0 or target >= self.nodes:
            return Err("Node index boundaries are structurally invalid.")
        if weight < 0.0:
            return Err("Algorithm assumes non-negative structural weights.")
            
        try:
            self.adj_matrix[source, target] = weight
            if not directed:
                self.adj_matrix[target, source] = weight
            return Ok(True)
        except Exception as e:
            return Err(f"Structural edge parsing failed: {e}")

    def shortest_path(self, origin: int) -> Result:
        """
        Dijkstra deterministic resolution loop executing entirely over Numpy vectors.
        Retrieves minimum traversal bounds from 'origin' to all interconnected graph nodes.
        Returns array of min-distances of size (nodes,).
        """
        if origin < 0 or origin >= self.nodes:
            return Err("Origin indexing out of dimension boundary.")
            
        try:
            distances = np.full(self.nodes, np.inf, dtype=np.float64)
            visited = np.zeros(self.nodes, dtype=bool)
            
            distances[origin] = 0.0
            
            for _ in range(self.nodes):
                # Mask out visited nodes by artificially raising distance
                unvisited_dists = np.where(visited, np.inf, distances)
                current = int(np.argmin(unvisited_dists))
                
                # If the remaining unvisited are all unreachable
                if np.isinf(unvisited_dists[current]):
                    break
                    
                visited[current] = True
                
                # Update distances directly using vectorized adj_matrix row
                # new_dists = dists[current] + adj_matrix[current, :]
                potential_paths = distances[current] + self.adj_matrix[current]
                
                # Element-wise minimum swap across all unvisited
                distances = np.minimum(distances, potential_paths)
                
            return Ok(distances)
            
        except Exception as e:
            return Err(f"Graph extraction fault: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniAlgoWikiEngine:
    """
    Production Engine for Dense Algorithmic Parsing.
    """

    def __init__(self, config=None):
        """Initialize OmniAlgoWikiEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-algowiki"

    def init_graph(self, size: int) -> GraphResolver:
        """Performs init graph operation for OmniAlgoWikiEngine."""
        return GraphResolver(node_count=size)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniAlgoWikiEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic Adjacency Shortest Path",
            "status": "operational",
        }
