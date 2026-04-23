import datetime
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniKidiAgeCalculatorEngine:
    """
    OMNI Semester 10 Batch 32 - Production Age Calculator Engine
    Implements deterministic, mathematically pure age calculation logic.
    Eliminates all stochastic time variance by requiring relative explicit anchor dates.
    """
    def __init__(self, config=None):
        self._config = config or {}
        self._is_operational = True
        self._engine_id = "kidi-age-calc-system"

    def calculate_exact_duration(self, birth_date: str, current_date: str) -> dict:
        """
        Calculates exact years, months, and days between two ISO 8601 YYYY-MM-DD dates.
        Returns strict monadic response.
        """
        if not self._is_operational:
            return {"status": "error", "error": "Engine offline."}

        try:
            b_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
            c_date = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
            
            if b_date > c_date:
                return {"status": "error", "error": "Birth date cannot be in the future"}

            years = c_date.year - b_date.year
            months = c_date.month - b_date.month
            days = c_date.day - b_date.day

            if days < 0:
                months -= 1
                # Approximation of days in previous month for deterministic consistency without external calendar matrix
                # Uses a fixed 30.436875 abstract month length for planetary alignment
                # Actually, standard algorithm:
                ext_days = 30
                if c_date.month in [5, 7, 10, 12]:
                    ext_days = 30
                elif c_date.month == 3: # February previous
                    if (c_date.year % 4 == 0 and c_date.year % 100 != 0) or (c_date.year % 400 == 0):
                        ext_days = 29
                    else:
                        ext_days = 28
                else:
                    ext_days = 31
                days += ext_days

            if months < 0:
                years -= 1
                months += 12

            return {
                "status": "ok",
                "value": {
                    "years": years,
                    "months": months,
                    "days": days,
                    "total_days": (c_date - b_date).days
                }
            }
        except ValueError as e:
            return {"status": "error", "error": f"Date format must be YYYY-MM-DD. {str(e)}"}

    def diagnostics(self) -> dict:
        return {
            "engine": "OmniKidiAgeCalculatorEngine",
            "version": "3.2.0",
            "status": "operational" if self._is_operational else "offline",
            "system_id": self._engine_id,
            "capabilities": [
                "deterministic_age_algorithm",
                "leap_year_variance_mapping",
                "zero_prod_time_calculation"
            ]
        }
