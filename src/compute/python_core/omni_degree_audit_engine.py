"""OmniDegreeAuditEngine for aggregating structural credits."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniDegreeAuditEngine(OmniBaseEngine):
    """Production-grade Omni Degree Audit Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def audit(self, completed_courses: List[Dict[str, Any]], rules: Dict[str, Any]) -> Result[Dict[str, Any], str]:
        """
        Audits completed courses against degree requirements.
        completed_courses items need 'id', 'category', 'credits'.
        rules dict maps 'category' -> minimum_credits_required.
        """
        try:
            if not isinstance(completed_courses, list) or not isinstance(rules, dict):
                return Result.fail("Invalid input types")

            category_sums: Dict[str, int] = {cat: 0 for cat in rules.keys()}
            total_credits = 0

            # Compute actuals
            for course in completed_courses:
                cat = course.get('category')
                creds = course.get('credits', 0)
                if cat in category_sums:
                    category_sums[cat] += creds
                total_credits += creds

            # Audit against rules
            deficiencies = {}
            is_graduating = True

            for cat, min_required in rules.items():
                shortfall = min_required - category_sums[cat]
                if shortfall > 0:
                    deficiencies[cat] = shortfall
                    is_graduating = False

            return Result.ok({
                "total_credits": total_credits,
                "category_sums": category_sums,
                "deficiencies": deficiencies,
                "eligible_for_graduation": is_graduating
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniDegreeAuditEngine",
            "status": "operational",
            "complexity": "O(N)"
        }
