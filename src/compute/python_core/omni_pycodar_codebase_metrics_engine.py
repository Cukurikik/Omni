"""OmniPycodarCodebaseMetricsEngine — Codebase Structure Analysis & Metrics.

Inspired by QuentinWach/PyCodar: a CLI tool that summarizes a Python
codebase by traversing its file tree, counting lines, functions, classes,
and methods, and displaying the structure as a colored tree.

Algorithmic Primitive:
    Given a file tree representation, compute aggregate metrics:
    total lines, total files, average lines per file, maximum depth,
    and identify the largest files. Also detect potential dead code
    by finding files with zero public functions.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniPycodarCodebaseMetricsEngine:
    """Production-grade codebase structure analysis and metrics engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniPycodarCodebaseMetricsEngine",
            "version": "1.0.0",
            "primitive": "recursive_file_tree_metrics_aggregation",
            "monadic_enforcement": True,
            "source_repo": "QuentinWach/PyCodar",
        }

    @staticmethod
    def compute_metrics(file_tree: list[dict]) -> Result:
        """Compute aggregate codebase metrics from a file tree.

        Args:
            file_tree: List of file descriptors, each with:
                - 'path': str — file path
                - 'lines': int — number of lines
                - 'functions': int — number of functions/methods
                - 'classes': int — number of classes

        Returns:
            Result[dict, Exception]: dict with 'total_files', 'total_lines',
            'total_functions', 'total_classes', 'avg_lines_per_file',
            'largest_file', 'smallest_file'.
        """
        if not isinstance(file_tree, list) or len(file_tree) == 0:
            return Err(Exception("file_tree must be a non-empty list of file descriptors"))

        total_lines = 0
        total_functions = 0
        total_classes = 0
        largest = None
        smallest = None

        for f in file_tree:
            if not isinstance(f, dict):
                return Err(Exception("Each file descriptor must be a dict"))
            if "path" not in f or "lines" not in f:
                return Err(Exception(f"File descriptor missing 'path' or 'lines'"))
            if f["lines"] < 0:
                return Err(Exception(f"File '{f['path']}' has negative line count"))

            total_lines += f["lines"]
            total_functions += f.get("functions", 0)
            total_classes += f.get("classes", 0)

            if largest is None or f["lines"] > largest["lines"]:
                largest = f
            if smallest is None or f["lines"] < smallest["lines"]:
                smallest = f

        avg = round(total_lines / len(file_tree), 2)

        return Ok({
            "total_files": len(file_tree),
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "avg_lines_per_file": avg,
            "largest_file": {"path": largest["path"], "lines": largest["lines"]},
            "smallest_file": {"path": smallest["path"], "lines": smallest["lines"]},
        })

    @staticmethod
    def detect_dead_code_candidates(file_tree: list[dict]) -> Result:
        """Identify files with zero public functions (potential dead code).

        Args:
            file_tree: Same format as compute_metrics.

        Returns:
            Result[list[str], Exception]: List of file paths with 0 functions.
        """
        if not isinstance(file_tree, list):
            return Err(Exception("file_tree must be a list"))

        candidates = [
            f["path"] for f in file_tree
            if isinstance(f, dict) and f.get("functions", 0) == 0
               and f.get("lines", 0) > 0
        ]

        return Ok(candidates)

    @staticmethod
    def compute_directory_depth(paths: list[str], separator: str = "/") -> Result:
        """Compute the maximum directory depth from a list of file paths.

        Args:
            paths: List of file path strings.
            separator: Path separator character.

        Returns:
            Result[int, Exception]: Maximum depth.
        """
        if not isinstance(paths, list) or len(paths) == 0:
            return Err(Exception("paths must be a non-empty list"))

        max_depth = 0
        for p in paths:
            depth = p.count(separator)
            if depth > max_depth:
                max_depth = depth

        return Ok(max_depth)
