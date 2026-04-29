"""OmniVtexGuidelineComplianceEngine — Weighted Rule Compliance Scoring.

Inspired by vtex/development-guidelines: a set of engineering standards
covering Git workflow, code review, testing, and deployment practices.

Algorithmic Primitive:
    Given a set of compliance rules each with a weight and a boolean pass/
    fail status, compute a weighted compliance score normalized to [0, 1].
    Also identify which rules are failing and compute a criticality vector.
"""
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniVtexGuidelineComplianceEngine:
    """Production-grade weighted compliance rule evaluation engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniVtexGuidelineComplianceEngine",
            "version": "1.0.0",
            "primitive": "weighted_compliance_score_computation",
            "monadic_enforcement": True,
            "source_repo": "vtex/development-guidelines",
        }

    @staticmethod
    def compute_compliance_score(
        rules: list[dict],
    ) -> Result:
        """Compute a weighted compliance score.

        Args:
            rules: List of dicts, each with:
                - 'name': str — rule identifier
                - 'weight': float — importance weight (must be > 0)
                - 'passed': bool — whether the rule is satisfied

        Returns:
            Result[dict, Exception]: dict with 'score' (0.0 to 1.0),
            'passed_count', 'failed_count', 'failed_rules', 'total_weight'.
        """
        if not isinstance(rules, list) or len(rules) == 0:
            return Err(Exception("rules must be a non-empty list of rule dicts"))

        total_weight = 0.0
        earned_weight = 0.0
        failed_rules: list[str] = []
        passed_count = 0
        failed_count = 0

        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                return Err(Exception(f"Rule at index {i} must be a dict"))
            if "name" not in rule or "weight" not in rule or "passed" not in rule:
                return Err(Exception(f"Rule at index {i} missing required fields: name, weight, passed"))
            if rule["weight"] <= 0:
                return Err(Exception(f"Rule '{rule['name']}' has non-positive weight {rule['weight']}"))

            total_weight += rule["weight"]
            if rule["passed"]:
                earned_weight += rule["weight"]
                passed_count += 1
            else:
                failed_rules.append(rule["name"])
                failed_count += 1

        score = round(earned_weight / total_weight, 6)

        return Ok({
            "score": score,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "failed_rules": failed_rules,
            "total_weight": total_weight,
        })

    @staticmethod
    def meets_threshold(
        rules: list[dict],
        threshold: float,
    ) -> Result:
        """Check whether the compliance score meets a minimum threshold.

        Args:
            rules: Same format as compute_compliance_score.
            threshold: Minimum required score (0.0 to 1.0).

        Returns:
            Result[bool, Exception]: True if score >= threshold.
        """
        if not (0.0 <= threshold <= 1.0):
            return Err(Exception(f"Threshold must be in [0.0, 1.0], got {threshold}"))

        score_result = OmniVtexGuidelineComplianceEngine.compute_compliance_score(rules)
        if not score_result.is_ok():
            return Err(score_result.unwrap_err())

        data = score_result.unwrap()
        if data["score"] >= threshold:
            return Ok(True)
        else:
            return Err(Exception(
                f"Compliance score {data['score']:.4f} below threshold {threshold}. "
                f"Failing rules: {data['failed_rules']}"
            ))
