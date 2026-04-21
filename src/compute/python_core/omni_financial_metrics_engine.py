"""
OMNI Financial Metrics Engine
=============================
Production-grade abstraction inspired by shashankvemuri/Finance.
Stripped of external data pulling to isolate deterministically accurate 
amortization arrays mathematically mimicking financial bonds matrices.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class FinanceCalculusError(Exception):
    """Base error for Amortization abstractions."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. FIN-MATH AMORTIZATION MATRIX
# ---------------------------------------------------------------------------

class AmortizationCalculus:
    """Computes matrices of periodized financial bonds strictly inside Numpy."""
    
    def compute_schedule(self, principal: float, annual_rate: float, years: int) -> Result:
        """
        Generates full repayment mathematical tensor structure mapping exact limits.
        """
        if principal <= 0 or annual_rate < 0 or years <= 0:
            return Err("Financial metric bonds inverted logic. Require positive parameters.")
            
        try:
            # Posi-Matrix mathematical equivalent of Amortization Formula
            # M = P [ r(1 + r)^n ] / [ (1 + r)^n - 1]
            n_months = years * 12
            monthly_rate = annual_rate / 12.0
            
            if monthly_rate == 0:
                monthly_payment = principal / n_months
            else:
                top = monthly_rate * math.pow((1 + monthly_rate), n_months)
                bot = math.pow((1 + monthly_rate), n_months) - 1
                monthly_payment = principal * (top / bot)
                
            # evaluates_structurally the bounds array tracking
            schedule = np.zeros((n_months, 3), dtype=np.float64) # [Principal, Interest, Balance]
            
            balance = principal
            for i in range(n_months):
                interest = balance * monthly_rate
                p_payment = monthly_payment - interest
                balance -= p_payment
                # Boundary safe lock
                if balance < 1e-5: balance = 0.0
                
                schedule[i] = [p_payment, interest, balance]
                
            return Ok({
                "monthly_payment": float(monthly_payment),
                "total_interest_paid": float(np.sum(schedule[:, 1])),
                "tensor_schedule_shape": schedule.shape
            })
            
        except Exception as e:
            return Err(f"Schedules calculation fracture error: {e}")

    def compute_compound_growth(self, principal: float, annual_rate: float, years: float, times_compounded: int = 12) -> Result:
        """Compute compound growth."""
        try:
            # A = P (1 + r/n)^(nt)
            rate_per_period = annual_rate / times_compounded
            total_periods = times_compounded * years
            
            amount = principal * math.pow((1 + rate_per_period), total_periods)
            return Ok(float(amount))
        except Exception as e:
            return Err(str(e))


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniFinancialMetricsEngine:
    """
    Production Engine for Deterministic Amortization Arrays.
    """

    def __init__(self, config=None):
        """Initialize OmniFinancialMetricsEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-financial-metrics"

    def get_calculus(self) -> AmortizationCalculus:
        """Performs get calculus operation for OmniFinancialMetricsEngine."""
        return AmortizationCalculus()

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniFinancialMetricsEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic NumPy Amortization Periodization Matrix",
            "status": "operational",
        }
