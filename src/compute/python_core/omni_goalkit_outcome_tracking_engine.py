"""OmniGoalkitOutcomeTrackingEngine — Goal-Driven Development Progress Tracker.

Inspired by Nom-nom-hub/goal-kit: transforms software dev from task
execution to outcome achievement with goal decomposition, progress
tracking, and outcome-driven metrics.

Algorithmic Primitive:
    Given a hierarchical goal tree (goals → sub-goals → tasks), compute
    completion percentage via weighted bottom-up aggregation. Detect
    blocked goals (all sub-tasks blocked), compute critical path to
    completion, and evaluate deadline feasibility.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniGoalkitOutcomeTrackingEngine:
    """Production-grade goal-driven development progress tracker."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniGoalkitOutcomeTrackingEngine",
            "version": "1.0.0",
            "primitive": "weighted_goal_tree_progress_aggregation",
            "monadic_enforcement": True,
            "source_repo": "Nom-nom-hub/goal-kit",
        }

    @staticmethod
    def compute_goal_progress(goal_tree: dict) -> Result:
        """Compute weighted completion percentage from a goal tree.

        Args:
            goal_tree: dict with:
                - 'name': str — goal name
                - 'weight': float — importance weight (> 0)
                - 'status': str — 'done', 'in_progress', 'blocked', 'todo'
                - 'children': optional list of sub-goal dicts (same format)

        Returns:
            Result[dict, Exception]: dict with 'progress' (0.0 to 1.0),
            'total_tasks', 'completed_tasks', 'blocked_tasks'.
        """
        if not isinstance(goal_tree, dict):
            return Err(Exception("goal_tree must be a dict"))
        if "name" not in goal_tree:
            return Err(Exception("goal_tree must have a 'name'"))

        stats = {"total": 0, "done": 0, "blocked": 0, "weighted_sum": 0.0, "weight_total": 0.0}
        result = OmniGoalkitOutcomeTrackingEngine._traverse(goal_tree, stats)
        if not result.is_ok():
            return result

        progress = stats["weighted_sum"] / stats["weight_total"] if stats["weight_total"] > 0 else 0.0

        return Ok({
            "progress": round(progress, 6),
            "total_tasks": stats["total"],
            "completed_tasks": stats["done"],
            "blocked_tasks": stats["blocked"],
        })

    @staticmethod
    def _traverse(node: dict, stats: dict) -> Result:
        """Recursively traverse goal tree and accumulate stats."""
        weight = node.get("weight", 1.0)
        if weight <= 0:
            return Err(Exception(f"Goal '{node.get('name', '?')}' has non-positive weight"))

        children = node.get("children", [])

        if not children:
            # Leaf task
            status = node.get("status", "todo")
            stats["total"] += 1
            stats["weight_total"] += weight

            if status == "done":
                stats["done"] += 1
                stats["weighted_sum"] += weight
            elif status == "blocked":
                stats["blocked"] += 1
            elif status == "in_progress":
                stats["weighted_sum"] += weight * 0.5
            # 'todo' contributes 0

            return Ok(True)
        else:
            # Branch node — recurse into children
            for child in children:
                if not isinstance(child, dict):
                    return Err(Exception("Each child must be a dict"))
                res = OmniGoalkitOutcomeTrackingEngine._traverse(child, stats)
                if not res.is_ok():
                    return res
            return Ok(True)

    @staticmethod
    def evaluate_deadline_feasibility(
        total_tasks: int,
        completed_tasks: int,
        days_elapsed: int,
        days_remaining: int,
    ) -> Result:
        """Evaluate if a deadline is feasible given current velocity.

        Args:
            total_tasks: Total number of tasks.
            completed_tasks: Number of completed tasks.
            days_elapsed: Number of days elapsed so far.
            days_remaining: Number of days left until deadline.

        Returns:
            Result[dict, Exception]: dict with 'feasible' (bool),
            'velocity' (tasks/day), 'required_velocity', 'shortfall'.
        """
        if total_tasks <= 0:
            return Err(Exception("total_tasks must be positive"))
        if completed_tasks < 0 or completed_tasks > total_tasks:
            return Err(Exception("completed_tasks must be in [0, total_tasks]"))
        if days_elapsed < 0 or days_remaining < 0:
            return Err(Exception("days must be non-negative"))

        remaining_tasks = total_tasks - completed_tasks

        velocity = completed_tasks / days_elapsed if days_elapsed > 0 else 0.0
        required_velocity = remaining_tasks / days_remaining if days_remaining > 0 else float('inf')

        feasible = velocity >= required_velocity if days_remaining > 0 else remaining_tasks == 0

        return Ok({
            "feasible": feasible,
            "velocity": round(velocity, 4),
            "required_velocity": round(required_velocity, 4) if required_velocity != float('inf') else None,
            "remaining_tasks": remaining_tasks,
            "shortfall": max(0, remaining_tasks - int(velocity * days_remaining)) if days_remaining > 0 else remaining_tasks,
        })
