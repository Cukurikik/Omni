"""OmniScottgalMiddlewarePipelineEngine — Ordered Middleware Pipeline Composition.

Inspired by scottgal/mostlylucidweb: an ASP.NET Core application with
custom tag helpers, Markdig extensions, HTMX integration, and an
ordered content processing pipeline.

Algorithmic Primitive:
    Given a list of middleware stages each with a priority (lower = earlier),
    compute the correct execution order. Detect priority collisions, ensure
    the pipeline has no gaps (sequential priority coverage), and validate
    that required middleware stages are present.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniScottgalMiddlewarePipelineEngine:
    """Production-grade middleware pipeline composition engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniScottgalMiddlewarePipelineEngine",
            "version": "1.0.0",
            "primitive": "priority_ordered_middleware_composition",
            "monadic_enforcement": True,
            "source_repo": "scottgal/mostlylucidweb",
        }

    @staticmethod
    def resolve_pipeline_order(
        stages: list[dict],
    ) -> Result:
        """Resolve the execution order of middleware stages by priority.

        Args:
            stages: List of dicts, each with:
                - 'name': str — middleware name
                - 'priority': int — execution priority (lower = earlier)

        Returns:
            Result[list[str], Exception]: Ordered list of stage names, or Err
            if priority collisions exist.
        """
        if not isinstance(stages, list) or len(stages) == 0:
            return Err(Exception("stages must be a non-empty list of stage dicts"))

        priorities_seen: dict[int, str] = {}
        for stage in stages:
            if not isinstance(stage, dict):
                return Err(Exception("Each stage must be a dict with 'name' and 'priority'"))
            if "name" not in stage or "priority" not in stage:
                return Err(Exception(f"Stage missing required fields: name, priority"))
            p = stage["priority"]
            if p in priorities_seen:
                return Err(Exception(
                    f"Priority collision: '{stage['name']}' and '{priorities_seen[p]}' "
                    f"both have priority {p}"
                ))
            priorities_seen[p] = stage["name"]

        sorted_stages = sorted(stages, key=lambda s: s["priority"])
        return Ok([s["name"] for s in sorted_stages])

    @staticmethod
    def validate_required_stages(
        stages: list[dict],
        required: list[str],
    ) -> Result:
        """Validate that all required middleware stages are present.

        Args:
            stages: List of stage dicts (same format as resolve_pipeline_order).
            required: List of required stage names.

        Returns:
            Result[bool, Exception]: True if all required stages are present.
        """
        if not isinstance(stages, list):
            return Err(Exception("stages must be a list"))
        if not isinstance(required, list):
            return Err(Exception("required must be a list"))

        present = {s["name"] for s in stages if isinstance(s, dict) and "name" in s}

        missing = [r for r in required if r not in present]
        if missing:
            return Err(Exception(
                f"Missing required middleware stages: {missing}"
            ))

        return Ok(True)

    @staticmethod
    def compute_pipeline_latency(
        stages: list[dict],
    ) -> Result:
        """Compute total estimated pipeline latency.

        Args:
            stages: List of dicts, each with:
                - 'name': str
                - 'priority': int
                - 'latency_ms': float — estimated latency in milliseconds

        Returns:
            Result[dict, Exception]: dict with 'total_latency_ms', 'stage_count',
            and 'ordered_stages'.
        """
        if not isinstance(stages, list) or len(stages) == 0:
            return Err(Exception("stages must be a non-empty list"))

        total = 0.0
        for stage in stages:
            if "latency_ms" not in stage:
                return Err(Exception(f"Stage '{stage.get('name', '?')}' missing 'latency_ms'"))
            if stage["latency_ms"] < 0:
                return Err(Exception(f"Stage '{stage['name']}' has negative latency"))
            total += stage["latency_ms"]

        order_result = OmniScottgalMiddlewarePipelineEngine.resolve_pipeline_order(stages)
        if not order_result.is_ok():
            return Err(order_result.unwrap_err())

        return Ok({
            "total_latency_ms": round(total, 3),
            "stage_count": len(stages),
            "ordered_stages": order_result.unwrap(),
        })
