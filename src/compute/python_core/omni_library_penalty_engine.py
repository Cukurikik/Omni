"""OmniLibraryPenaltyEngine for calculating mathematical late fee sequences."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniLibraryPenaltyEngine(OmniBaseEngine):
    """Production-grade Omni Library Penalty Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def calculate_penalty(self, days_late: int, base_fee: float, max_fee: float, multiplier: float) -> Result[Dict[str, Any], str]:
        """
        Calculates compounded library penalties deterministically.
        If multiplier > 1.0, fee compounds every late day. 
        Multiplier of 1.0 means flat addition.
        """
        try:
            if days_late < 0:
                return Result.fail("Days late cannot be negative")
            if base_fee < 0 or max_fee < 0:
                return Result.fail("Fees cannot be negative")

            if days_late == 0:
                return Result.ok({
                    "days_late": 0,
                    "penalty_applied": 0.0,
                    "is_maxed": False
                })

            current_fee = 0.0
            
            if multiplier == 1.0:
                current_fee = base_fee * days_late
            else:
                # Geometric progression for compound late fees
                current_fee = base_fee * ((multiplier ** days_late - 1) / (multiplier - 1))

            is_maxed = False
            if current_fee >= max_fee:
                current_fee = max_fee
                is_maxed = True

            return Result.ok({
                "days_late": days_late,
                "penalty_applied": current_fee,
                "is_maxed": is_maxed
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniLibraryPenaltyEngine",
            "status": "operational",
            "complexity": "O(1)"
        }
