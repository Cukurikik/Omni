"""OmniSalaryAnalyticsEngine — Interactive Salary Distribution & Percentiles.

Inspired by kadirermantr/getsalary: an interactive salary analytics
dashboard for Türkiye's software industry.

Algorithmic Primitive:
    Aggregate raw salary survey data across dimensions (role, experience),
    and compute statistical distributions including min, max, mean, and
    the 25th, 50th (median), and 75th percentiles to provide robust
    market baseline metrics.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniSalaryAnalyticsEngine:
    """Production-grade salary statistics and percentile analytics engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniSalaryAnalyticsEngine",
            "version": "1.0.0",
            "primitive": "salary_percentile_distribution_analytics",
            "monadic_enforcement": True,
            "source_repo": "kadirermantr/getsalary",
        }

    @staticmethod
    def compute_percentiles(salaries: list[float]) -> Result:
        """Compute structural percentile distributions of a salary pool.

        Args:
            salaries: List of floats representing salaries.

        Returns:
            Result[dict, Exception]: dict mapping 'p25', 'median', 'p75',
            'mean', 'min', 'max', 'count'.
        """
        if not isinstance(salaries, list):
            return Err(Exception("salaries must be a list"))
        if len(salaries) == 0:
            return Err(Exception("salaries list cannot be empty"))

        valid_salaries = []
        for s in salaries:
            if not isinstance(s, (int, float)):
                return Err(Exception("All salaries must be valid numbers"))
            if s < 0:
                return Err(Exception("Salaries must be non-negative"))
            valid_salaries.append(float(s))

        sorted_sal = sorted(valid_salaries)
        n = len(sorted_sal)

        def _get_percentile(data: list[float], p: float) -> float:
            index = (len(data) - 1) * p
            lower = int(index)
            upper = lower + 1
            weight = index - lower
            if upper >= len(data):
                return data[lower]
            return round(data[lower] * (1 - weight) + data[upper] * weight, 2)

        mean = round(sum(sorted_sal) / n, 2)
        p25 = _get_percentile(sorted_sal, 0.25)
        median = _get_percentile(sorted_sal, 0.50)
        p75 = _get_percentile(sorted_sal, 0.75)

        return Ok({
            "count": n,
            "min": sorted_sal[0],
            "p25": p25,
            "median": median,
            "mean": mean,
            "p75": p75,
            "max": sorted_sal[-1],
        })

    @staticmethod
    def aggregate_by_role(survey_data: list[dict]) -> Result:
        """Aggregate salary data grouped by job role.

        Args:
            survey_data: List of dicts with 'role' (str) and 'salary' (float).

        Returns:
            Result[dict, Exception]: Dictionary mapping role names to their
            computed distribution statistics.
        """
        if not isinstance(survey_data, list):
            return Err(Exception("survey_data must be a list"))

        group_map: dict[str, list[float]] = {}
        for entry in survey_data:
            if not isinstance(entry, dict):
                return Err(Exception("Each survey entry must be a dictionary"))
            role = entry.get("role", "Unknown")
            salary = entry.get("salary")
            if salary is None:
                continue
            if role not in group_map:
                group_map[role] = []
            group_map[role].append(float(salary))

        aggregated: dict[str, dict] = {}
        for role, sal_list in group_map.items():
            if len(sal_list) > 0:
                res = OmniSalaryAnalyticsEngine.compute_percentiles(sal_list)
                if not res.is_ok():
                    return Err(Exception(f"Failed aggregating role '{role}': {res.unwrap_err()}"))
                aggregated[role] = res.unwrap()

        return Ok(aggregated)
