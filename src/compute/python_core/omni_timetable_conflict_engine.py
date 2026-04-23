"""OmniTimetableConflictEngine for deterministic interval overlap detection."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniTimetableConflictEngine(OmniBaseEngine):
    """Production-grade Omni Timetable Conflict Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def detect_conflicts(self, schedules: List[Dict[str, Any]]) -> Result[Dict[str, Any], str]:
        """
        Detects overlaps in time intervals.
        Schedules must have 'id', 'start', 'end'. (start and end as integers e.g. minutes from midnight).
        """
        try:
            for s in schedules:
                if 'id' not in s or 'start' not in s or 'end' not in s:
                    return Result.fail("Each schedule must have 'id', 'start', and 'end'")
                if s['start'] >= s['end']:
                    return Result.fail(f"Invalid interval for {s['id']}: start >= end")

            # Sort by start time. Deterministic fallback to end time, then id.
            sorted_schedules = sorted(schedules, key=lambda x: (x['start'], x['end'], x['id']))
            conflicts = []

            for i in range(len(sorted_schedules) - 1):
                curr = sorted_schedules[i]
                nxt = sorted_schedules[i + 1]
                
                # Check overlap (strict overlap: current end > next start)
                if curr['end'] > nxt['start']:
                    conflicts.append((curr['id'], nxt['id']))

            return Result.ok({
                "has_conflict": len(conflicts) > 0,
                "conflicts": conflicts
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniTimetableConflictEngine",
            "status": "operational",
            "complexity": "O(N log N)"
        }
