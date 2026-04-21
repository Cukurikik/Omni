# ===========================================================================
# OMNI QUANT FINANCE ENGINE (SEMESTER 5 — BATCH 9)
# ===========================================================================
# Absorbed From  : microsoft/qlib
# Logic Inherited: Compute Layer (AI-Oriented Quantitative Finance)
# ===========================================================================
"""
OMNI Quant Finance Engine
=========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
from typing import Dict, Any, List


ENGINE_VERSION = "1.0.0-omni"

logger = logging.getLogger("OmniQuantFinanceEngine")

class OmniQuantFinanceEngine:
    """
    Financial time series processing: Moving Averages, Alpha signal generation,
    and offline paper-trading backtester.
    """

    def __init__(self):
        """Initialize OmniQuantFinanceEngine."""
        self._is_ready = True

    def calculate_moving_average(self, prices: List[float], window: int = 5) -> Dict[str, Any]:
        """Calculates Simple Moving Average (SMA)."""
        if not prices or window <= 0 or len(prices) < window:
            return {"status": "error", "error": "Invalid price series or window."}
        ma = []
        for i in range(len(prices) - window + 1):
            ma.append(round(sum(prices[i:i+window]) / window, 4))
        return {"status": "success", "data": {"ma_window": window, "values": ma}}

    def generate_alpha_signal(self, price: float, ma_fast: float, ma_slow: float) -> Dict[str, Any]:
        """Generates a trading signal based on MA crossover."""
        if ma_fast > ma_slow:
            signal, action = 1.0, "BUY"
        elif ma_fast < ma_slow:
            signal, action = -1.0, "SELL"
        else:
            signal, action = 0.0, "HOLD"
        strength = abs(ma_fast - ma_slow) / price if price > 0 else 0
        return {"status": "success", "data": {"signal": signal, "action": action, "strength": round(strength, 6)}}

    def run_paper_backtester(self, prices: List[float], fast_w: int = 3, slow_w: int = 7) -> Dict[str, Any]:
        """Runs a paper trading topological_evaluation over historical prices."""
        fast_r = self.calculate_moving_average(prices, fast_w)
        slow_r = self.calculate_moving_average(prices, slow_w)
        if fast_r["status"] == "error" or slow_r["status"] == "error":
            return {"status": "error", "error": "Insufficient data for backtesting."}
        fast_ma, slow_ma = fast_r["data"]["values"], slow_r["data"]["values"]
        offset = slow_w - fast_w
        aligned_fast = fast_ma[offset:]
        aligned_prices = prices[slow_w - 1:]
        capital, position = 10000.0, 0.0
        for i in range(min(len(aligned_prices), len(aligned_fast), len(slow_ma))):
            sig = self.generate_alpha_signal(aligned_prices[i], aligned_fast[i], slow_ma[i])
            act = sig["data"]["action"]
            if act == "BUY" and position == 0:
                position = capital / aligned_prices[i]
                capital = 0.0
            elif act == "SELL" and position > 0:
                capital = position * aligned_prices[i]
                position = 0.0
        if position > 0:
            capital = position * aligned_prices[-1]
        return {"status": "success", "data": {"initial": 10000.0, "final": round(capital, 2),
                "profit_pct": round(((capital - 10000) / 10000) * 100, 2)}}

    def evaluate_health(self) -> Dict[str, Any]:
        """Performs evaluate health operation for OmniQuantFinanceEngine."""
        return {"engine": "OmniQuantFinanceEngine", "layer": "Compute", "status": "healthy",
                "capabilities": ["SMA", "Alpha Signals", "Backtesting"], "learned_from": "microsoft/qlib"}

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-quant-finance",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
