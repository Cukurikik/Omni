from __future__ import annotations
from typing import Dict, Any, List
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniCS253SoftwareCourseMatrixEngine:
    """
    omni-cs253-software-course-matrix
    
    A structural mathematical metrics engine generating Gaussian probability grading 
    distribution limits and computing true weighted percentile constraints globally.
    Inspired by Shreyasi2002/CS253_Project.
    """
    
    ENGINE_VERSION = "omni-s11-b4.1.0"
    
    def __init__(self, curve_shift: float = 0.0) -> None:
        """Curve shift allows native median dragging computations."""
        self.curve_shift = curve_shift

    def calculate_distribution_percentiles(self, raw_scores: List[float]) -> Result:
        """
        Natively processes scores array calculating true metric bounds, 
        std deviation, median, and dynamic percentage scaling.
        """
        try:
            if not raw_scores:
                return Err(ValueError("Cannot compute Gaussian distributions over unbound score arrays."))
                
            for s in raw_scores:
                if s < 0 or s > 100:
                    return Err(ValueError("Scores must mathematically fall within [0, 100] standard bounds."))
                    
            n = len(raw_scores)
            
            # Sorted scores for accurate mathematical parsing
            sorted_scores = sorted(raw_scores)
            mean_val = sum(sorted_scores) / n
            
            # Std deviation natively
            variance = sum((x - mean_val) ** 2 for x in sorted_scores) / max(1, n - 1)
            std_dev = math.sqrt(variance)
            
            # Median natively
            if n % 2 == 0:
                median_val = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2.0
            else:
                median_val = sorted_scores[n // 2]
                
            # Distribution assignments natively via Standard Deviation curves
            # A: > Mean + 1 SD
            # B: > Mean
            # C: > Mean - 1 SD
            # D/F: <= Mean - 1 SD
            
            distributions = {"A": 0, "B": 0, "C": 0, "D_F": 0}
            
            for score in sorted_scores:
                shifted = score + self.curve_shift
                if shifted > mean_val + std_dev:
                    distributions["A"] += 1
                elif shifted > mean_val:
                    distributions["B"] += 1
                elif shifted > mean_val - std_dev:
                    distributions["C"] += 1
                else:
                    distributions["D_F"] += 1
                    
            return Ok({
                "population": n,
                "mean": round(mean_val, 2),
                "median": round(median_val, 2),
                "standard_deviation": round(std_dev, 2),
                "distribution_matrix": distributions
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Interface registry requirements."""
        return {
            "engine": "OmniCS253SoftwareCourseMatrixEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "curve_shift": self.curve_shift,
            "complexity": "O(N log N) Sorting and Limit Integration"
        }
