"""OmniFitnessMetricsEngine for evaluating tracking metrics and BMI."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniFitnessMetricsEngine(OmniBaseEngine):
    """Production-grade Omni Fitness Metrics Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def calculate_metrics(self, weight_kg: float, height_cm: float, daily_activities: List[Dict[str, Any]]) -> Result[Dict[str, Any], str]:
        """
        Calculates BMI and estimates total calorie burn.
        Activities must have: 'mets' (Metabolic Equivalent) and 'duration_min'.
        """
        try:
            if weight_kg <= 0 or height_cm <= 0:
                return Result.fail("Weight and height must be strictly positive")

            height_m = height_cm / 100.0
            bmi = weight_kg / (height_m * height_m)
            
            if bmi < 18.5:
                category = "underweight"
            elif bmi < 25.0:
                category = "normal"
            elif bmi < 30.0:
                category = "overweight"
            else:
                category = "obese"

            # Basal Metabolic Rate (simplified Mifflin-St Jeor rough constant)
            # Roughly 1 MET = 1 kcal/kg/hour -> 24 kcal/kg/day standard baseline
            bmr = weight_kg * 24.0
            
            active_calories = 0.0
            for act in daily_activities:
                mets = float(act.get('mets', 1.0))
                mins = float(act.get('duration_min', 0.0))
                # Calories = METs * weight (kg) * time (hrs)
                burned = mets * weight_kg * (mins / 60.0)
                active_calories += burned

            return Result.ok({
                "bmi": bmi,
                "category": category,
                "bmr_estimation": bmr,
                "active_calories_burned": active_calories,
                "total_daily_energy_expenditure": bmr + active_calories
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniFitnessMetricsEngine",
            "status": "operational"
        }
