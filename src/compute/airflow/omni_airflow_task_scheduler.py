# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Airflow Task Scheduler (OMNI Zero-Mock Implementation)
# Implements execution time sliding window logic for cron definitions.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[bool]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: bool) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AirflowCronEvaluator:
    def evaluate_cron_hit(self, cron_minute: List[int], cron_hour: List[int], now_minute: int, now_hour: int) -> Result:
        if now_minute < 0 or now_minute > 59:
            return Result.err("Invalid minute value provided.")
        if now_hour < 0 or now_hour > 23:
            return Result.err("Invalid hour value provided.")
            
        # Empty arrays signify '*' (all-inclusion)
        match_min = len(cron_minute) == 0 or now_minute in cron_minute
        match_hour = len(cron_hour) == 0 or now_hour in cron_hour
        
        if match_min and match_hour:
             return Result.ok(True)
             
        return Result.ok(False)
