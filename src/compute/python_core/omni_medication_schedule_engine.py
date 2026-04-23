"""OmniMedicationScheduleEngine for calculating recurring dosings."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniMedicationScheduleEngine(OmniBaseEngine):
    """Production-grade Omni Medication Schedule Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def generate_schedule(self, start_hour: int, interval_hours: int, total_doses: int) -> Result[Dict[str, Any], str]:
        """
        Generates a chronological dosing schedule strictly using 24-hour integers.
        """
        try:
            if start_hour < 0 or start_hour > 23:
                return Result.fail("Start hour must be between 0 and 23")
            if interval_hours <= 0:
                return Result.fail("Interval must be positive")
            if total_doses <= 0:
                return Result.fail("Total doses must be positive")

            schedule = []
            current_hour = start_hour
            day_offset = 0

            for i in range(total_doses):
                schedule.append({
                    "dose_number": i + 1,
                    "day_offset": day_offset,
                    "time_24h": f"{current_hour:02d}:00"
                })

                current_hour += interval_hours
                if current_hour >= 24:
                    day_offset += current_hour // 24
                    current_hour = current_hour % 24

            return Result.ok({
                "schedule": schedule,
                "total_days_spanned": schedule[-1]["day_offset"] + 1 if schedule else 0
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMedicationScheduleEngine",
            "status": "operational"
        }
