"""OmniJobMatcherEngine for scoring and ranking job applicants."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniJobMatcherEngine(OmniBaseEngine):
    """Production-grade Omni Job Matcher Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def rank_applicants(self, 
                        required_skills: List[str], 
                        applicants: List[Dict[str, Any]]) -> Result[List[Dict[str, Any]], str]:
        """
        Matches applicant skills against required skills using Jaccard Similarity.
        Returns ranked list of applicants.
        """
        try:
            if not required_skills:
                return Result.fail("At least one required skill is needed")

            req_set = set(s.lower() for s in required_skills)
            ranked = []

            for app in applicants:
                app_id = app.get('id', 'unknown')
                skills = app.get('skills', [])
                
                app_set = set(s.lower() for s in skills)
                
                # Jaccard index: Intersection over Union
                intersection = req_set.intersection(app_set)
                union = req_set.union(app_set)
                
                score = len(intersection) / len(union) if union else 0.0
                
                ranked.append({
                    "applicant_id": app_id,
                    "match_score": score,
                    "matched_skills": sorted(list(intersection)),
                    "missing_skills": sorted(list(req_set - app_set))
                })

            # Sort by score descending, then ID ascending
            ranked.sort(key=lambda x: (-x['match_score'], str(x['applicant_id'])))

            return Result.ok(ranked)
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniJobMatcherEngine",
            "status": "operational",
            "algorithm": "Jaccard Index"
        }
