"""OmniJanbogaertsMarkBatchPromptEngine — Batch Prompt Scheduling with Rate-Limiting.

Inspired by jan-bogaerts/mark: a tool that splits large corpora into text
fragments, builds prompts for each, and dispatches them to LLMs with
dependency-aware scheduling, caching, and concurrency control.

Algorithmic Primitive:
    Given a set of prompt tasks with inter-dependencies (a DAG), compute a
    valid topological execution order, enforce concurrency bounds (max
    parallel dispatches), and calculate optimal batch partitioning that
    respects a per-window rate limit (max requests per time window).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from collections import deque
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniJanbogaertsMarkBatchPromptEngine:
    """Production-grade batch prompt scheduler with DAG ordering and rate limiting."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniJanbogaertsMarkBatchPromptEngine",
            "version": "1.0.0",
            "primitive": "topological_batch_scheduling_with_rate_limit",
            "monadic_enforcement": True,
            "source_repo": "jan-bogaerts/mark",
        }

    @staticmethod
    def topological_sort(tasks: dict[str, list[str]]) -> Result:
        """Compute a valid topological execution order for prompt tasks.

        Args:
            tasks: dict mapping task_name -> list of dependency task names.

        Returns:
            Result[list[str], Exception]: Ordered list of task names, or Err
            if a cycle is detected.
        """
        if not isinstance(tasks, dict):
            return Err(Exception("tasks must be a dict[str, list[str]]"))

        # Build in-degree map
        in_degree: dict[str, int] = {t: 0 for t in tasks}
        adj: dict[str, list[str]] = {t: [] for t in tasks}

        for task, deps in tasks.items():
            for dep in deps:
                if dep not in tasks:
                    return Err(Exception(f"Unknown dependency '{dep}' referenced by task '{task}'"))
                adj[dep].append(task)
                in_degree[task] += 1

        # Kahn's algorithm
        queue: deque[str] = deque(t for t, d in in_degree.items() if d == 0)
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(tasks):
            return Err(Exception("Cycle detected in task dependency graph — cannot schedule"))

        return Ok(order)

    @staticmethod
    def compute_batch_windows(
        total_tasks: int,
        max_concurrent: int,
        rate_limit_per_window: int,
    ) -> Result:
        """Compute the number of dispatch windows needed.

        Args:
            total_tasks: Total number of prompt tasks.
            max_concurrent: Maximum parallel dispatches allowed.
            rate_limit_per_window: Max requests allowed per time window.

        Returns:
            Result[dict, Exception]: dict with 'windows', 'tasks_per_window',
            and 'effective_concurrency'.
        """
        if total_tasks <= 0:
            return Err(Exception("total_tasks must be positive"))
        if max_concurrent <= 0:
            return Err(Exception("max_concurrent must be positive"))
        if rate_limit_per_window <= 0:
            return Err(Exception("rate_limit_per_window must be positive"))

        effective = min(max_concurrent, rate_limit_per_window)
        windows = -(-total_tasks // effective)  # ceiling division

        return Ok({
            "windows": windows,
            "tasks_per_window": effective,
            "effective_concurrency": effective,
            "total_tasks": total_tasks,
        })

    @staticmethod
    def should_use_cache(
        input_hash_current: str,
        input_hash_cached: str,
    ) -> Result:
        """Determine whether a cached transformer result can be reused.

        A transformer should only re-execute if its input has changed since
        the last run. This mirrors Mark's caching strategy.

        Args:
            input_hash_current: Hash of the current input.
            input_hash_cached: Hash of the input when cache was created.

        Returns:
            Result[bool, Exception]: True if cache is valid (hashes match).
        """
        if not input_hash_current or not input_hash_cached:
            return Err(Exception("Input hashes must be non-empty strings"))
        return Ok(input_hash_current == input_hash_cached)
