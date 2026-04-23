"""OmniCrowvertConversionPipelineEngine — Graph-Based Format Conversion Path Finding.

Inspired by EduardoDosSantosFerreira/crowvert: a bulk file converter
supporting chains like txt→docx→pdf, svg→png, etc.

Algorithmic Primitive:
    Model supported format conversions as a directed graph. Given a source
    format and a target format, find the shortest conversion path using BFS.
    Validate that no conversion step is missing and compute the total
    estimated cost (in arbitrary units) of the conversion chain.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from collections import deque
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniCrowvertConversionPipelineEngine:
    """Production-grade format conversion path finder using BFS on a format graph."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniCrowvertConversionPipelineEngine",
            "version": "1.0.0",
            "primitive": "bfs_format_conversion_path_finding",
            "monadic_enforcement": True,
            "source_repo": "EduardoDosSantosFerreira/crowvert",
        }

    @staticmethod
    def find_conversion_path(
        edges: list[tuple[str, str, float]],
        source: str,
        target: str,
    ) -> Result:
        """Find the shortest conversion path from source to target format.

        Args:
            edges: List of (from_format, to_format, cost) tuples representing
                   supported direct conversions.
            source: The source file format (e.g. "txt").
            target: The target file format (e.g. "pdf").

        Returns:
            Result[dict, Exception]: dict with 'path' (list of formats) and
            'total_cost' (sum of edge costs along the path).
        """
        if not isinstance(edges, list):
            return Err(Exception("edges must be a list of (from, to, cost) tuples"))
        if not source or not target:
            return Err(Exception("source and target must be non-empty format strings"))
        if source == target:
            return Ok({"path": [source], "total_cost": 0.0})

        # Build adjacency list
        adj: dict[str, list[tuple[str, float]]] = {}
        all_formats: set[str] = set()
        for frm, to, cost in edges:
            if cost < 0:
                return Err(Exception(f"Negative cost {cost} for edge {frm}->{to} is invalid"))
            adj.setdefault(frm, []).append((to, cost))
            all_formats.add(frm)
            all_formats.add(to)

        if source not in all_formats:
            return Err(Exception(f"Source format '{source}' not found in conversion graph"))
        if target not in all_formats:
            return Err(Exception(f"Target format '{target}' not found in conversion graph"))

        # BFS for shortest path (fewest hops)
        visited: set[str] = {source}
        queue: deque[tuple[str, list[str], float]] = deque()
        queue.append((source, [source], 0.0))

        while queue:
            current, path, cost = queue.popleft()
            for neighbor, edge_cost in adj.get(current, []):
                if neighbor == target:
                    return Ok({
                        "path": path + [neighbor],
                        "total_cost": round(cost + edge_cost, 6),
                    })
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor], cost + edge_cost))

        return Err(Exception(
            f"No conversion path exists from '{source}' to '{target}'"
        ))

    @staticmethod
    def validate_direct_conversion(
        edges: list[tuple[str, str, float]],
        source: str,
        target: str,
    ) -> Result:
        """Check if a direct (single-step) conversion exists.

        Returns:
            Result[float, Exception]: The cost of the direct conversion, or Err.
        """
        if not isinstance(edges, list):
            return Err(Exception("edges must be a list of (from, to, cost) tuples"))

        for frm, to, cost in edges:
            if frm == source and to == target:
                return Ok(cost)

        return Err(Exception(
            f"No direct conversion available from '{source}' to '{target}'"
        ))
