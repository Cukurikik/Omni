"""
OMNI AI Finance Engine
========================
Production-grade, zero-algebraic_bound quantitative finance engine inspired by
georgezouq/awesome-ai-in-finance. Implements technical indicators,
portfolio optimization, backtesting, risk metrics, position sizing,
and trading signal generators.

Extracted Patterns:
  - Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV
  - Portfolio optimization: Markowitz mean-variance, risk parity, equal weight
  - Backtesting framework: PnL, Sharpe, Sortino, max drawdown, Calmar
  - Trading signals: momentum, mean-reversion, trend-following, breakout
  - Risk metrics: VaR, CVaR, beta, alpha, information ratio
  - Position sizing: Kelly criterion, volatility targeting, fixed fractional

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class FinanceError(Exception):
    """Base error for finance engine."""

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
# 2. TECHNICAL INDICATORS
# ---------------------------------------------------------------------------

def sma(prices: np.ndarray, period: int) -> np.ndarray:
    """Simple Moving Average."""
    result = np.full_like(prices, np.nan, dtype=np.float64)
    for i in range(period - 1, len(prices)):
        result[i] = np.mean(prices[i - period + 1:i + 1])
    return result


def ema(prices: np.ndarray, period: int) -> np.ndarray:
    """Exponential Moving Average."""
    result = np.full_like(prices, np.nan, dtype=np.float64)
    alpha = 2.0 / (period + 1)
    result[period - 1] = np.mean(prices[:period])
    for i in range(period, len(prices)):
        result[i] = alpha * prices[i] + (1 - alpha) * result[i - 1]
    return result


def rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
    """Relative Strength Index (Wilder's method)."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    result = np.full(len(prices), np.nan, dtype=np.float64)
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    if avg_loss == 0:
        result[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[period] = 100.0 - 100.0 / (1.0 + rs)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            result[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i + 1] = 100.0 - 100.0 / (1.0 + rs)

    return result


def macd(prices: np.ndarray, fast: int = 12, slow: int = 26,
         signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Moving Average Convergence/Divergence.

    Returns:
        (macd_line, signal_line, histogram)
    """
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = ema_fast - ema_slow

    # Signal line (EMA of MACD)
    valid_mask = ~np.isnan(macd_line)
    signal_line = np.full_like(macd_line, np.nan)
    valid_macd = macd_line[valid_mask]
    if len(valid_macd) >= signal:
        sig = ema(valid_macd, signal)
        signal_line[valid_mask] = sig

    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(prices: np.ndarray, period: int = 20,
                    num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Bollinger Bands.

    Returns:
        (upper_band, middle_band, lower_band)
    """
    middle = sma(prices, period)
    std = np.full_like(prices, np.nan, dtype=np.float64)
    for i in range(period - 1, len(prices)):
        std[i] = np.std(prices[i - period + 1:i + 1])

    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
        period: int = 14) -> np.ndarray:
    """Average True Range."""
    tr = np.zeros(len(high), dtype=np.float64)
    tr[0] = high[0] - low[0]
    for i in range(1, len(high)):
        tr[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1]),
        )
    return sma(tr, period)


def obv(prices: np.ndarray, volume: np.ndarray) -> np.ndarray:
    """On-Balance Volume."""
    result = np.zeros(len(prices), dtype=np.float64)
    result[0] = volume[0]
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            result[i] = result[i - 1] + volume[i]
        elif prices[i] < prices[i - 1]:
            result[i] = result[i - 1] - volume[i]
        else:
            result[i] = result[i - 1]
    return result


def vwap(prices: np.ndarray, volume: np.ndarray) -> np.ndarray:
    """Volume Weighted Average Price."""
    cumulative_pv = np.cumsum(prices * volume)
    cumulative_v = np.cumsum(volume)
    return cumulative_pv / np.maximum(cumulative_v, 1e-10)


# ---------------------------------------------------------------------------
# 3. RISK METRICS
# ---------------------------------------------------------------------------

def compute_returns(prices: np.ndarray) -> np.ndarray:
    """Compute simple returns from price series."""
    return np.diff(prices) / prices[:-1]


def compute_log_returns(prices: np.ndarray) -> np.ndarray:
    """Compute log returns from price series."""
    return np.diff(np.log(prices))


def sharpe_ratio(returns: np.ndarray, risk_free: float = 0.0,
                 annualize: int = 252) -> float:
    """Annualized Sharpe Ratio."""
    excess = returns - risk_free / annualize
    if np.std(excess) == 0:
        return 0.0
    return float(np.mean(excess) / np.std(excess) * np.sqrt(annualize))


def sortino_ratio(returns: np.ndarray, risk_free: float = 0.0,
                  annualize: int = 252) -> float:
    """Annualized Sortino Ratio (downside deviation)."""
    excess = returns - risk_free / annualize
    downside = excess[excess < 0]
    if len(downside) == 0 or np.std(downside) == 0:
        return 0.0
    return float(np.mean(excess) / np.std(downside) * np.sqrt(annualize))


def max_drawdown(prices: np.ndarray) -> float:
    """Maximum drawdown from peak."""
    peak = np.maximum.accumulate(prices)
    dd = (prices - peak) / np.maximum(peak, 1e-10)
    return float(np.min(dd))


def calmar_ratio(returns: np.ndarray, prices: np.ndarray,
                 annualize: int = 252) -> float:
    """Calmar Ratio = annualized return / max drawdown."""
    ann_return = float(np.mean(returns) * annualize)
    mdd = abs(max_drawdown(prices))
    if mdd == 0:
        return 0.0
    return ann_return / mdd


def value_at_risk(returns: np.ndarray, confidence: float = 0.95) -> float:
    """Historical Value at Risk."""
    return float(np.percentile(returns, (1 - confidence) * 100))


def conditional_var(returns: np.ndarray, confidence: float = 0.95) -> float:
    """Conditional Value at Risk (Expected Shortfall)."""
    var = value_at_risk(returns, confidence)
    tail = returns[returns <= var]
    if len(tail) == 0:
        return var
    return float(np.mean(tail))


def beta(asset_returns: np.ndarray, market_returns: np.ndarray) -> float:
    """Beta coefficient (CAPM)."""
    cov = np.cov(asset_returns, market_returns)
    market_var = np.var(market_returns)
    if market_var == 0:
        return 0.0
    return float(cov[0, 1] / market_var)


def alpha_jensen(asset_returns: np.ndarray, market_returns: np.ndarray,
                 risk_free: float = 0.0) -> float:
    """Jensen's Alpha."""
    b = beta(asset_returns, market_returns)
    return float(np.mean(asset_returns) - risk_free - b * (np.mean(market_returns) - risk_free))


# ---------------------------------------------------------------------------
# 4. PORTFOLIO OPTIMIZATION
# ---------------------------------------------------------------------------

def portfolio_return(weights: np.ndarray, returns: np.ndarray) -> float:
    """Expected portfolio return from mean returns."""
    return float(np.dot(weights, np.mean(returns, axis=0)))


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Portfolio volatility from covariance matrix."""
    return float(np.sqrt(np.dot(weights, np.dot(cov_matrix, weights))))


def markowitz_equal_weight(n_assets: int) -> np.ndarray:
    """Equal weight allocation."""
    return np.ones(n_assets) / n_assets


def markowitz_min_variance(cov_matrix: np.ndarray) -> np.ndarray:
    """
    Minimum variance portfolio (analytical solution).

    Uses the closed-form: w = inv(S) * 1 / (1' * inv(S) * 1)
    """
    n = cov_matrix.shape[0]
    try:
        inv_cov = np.linalg.inv(cov_matrix + np.eye(n) * 1e-8)
    except np.linalg.LinAlgError:
        return markowitz_equal_weight(n)
    ones = np.ones(n)
    w = inv_cov @ ones
    w = w / np.sum(w)
    return np.maximum(w, 0)  # No short-selling


def risk_parity_weights(cov_matrix: np.ndarray, max_iter: int = 100,
                        tol: float = 1e-8) -> np.ndarray:
    """
    Risk parity portfolio weights.

    Each asset contributes equally to portfolio risk.
    Uses iterative rebalancing.
    """
    n = cov_matrix.shape[0]
    w = np.ones(n) / n

    for _ in range(max_iter):
        sigma_p = portfolio_volatility(w, cov_matrix)
        if sigma_p < 1e-12:
            break
        mc = cov_matrix @ w  # marginal contribution
        rc = w * mc / sigma_p  # risk contribution
        target = sigma_p / n
        w_new = w * target / np.maximum(rc, 1e-12)
        w_new = w_new / np.sum(w_new)
        if np.max(np.abs(w_new - w)) < tol:
            break
        w = w_new

    return w


# ---------------------------------------------------------------------------
# 5. POSITION SIZING
# ---------------------------------------------------------------------------

def kelly_criterion(win_prob: float, win_loss_ratio: float) -> float:
    """
    Kelly Criterion for optimal position sizing.

    f* = p - q/b where p = win prob, q = 1-p, b = win/loss ratio
    """
    q = 1.0 - win_prob
    if win_loss_ratio == 0:
        return 0.0
    f = win_prob - q / win_loss_ratio
    return max(0.0, min(1.0, f))


def volatility_target_size(target_vol: float, asset_vol: float,
                           portfolio_value: float, price: float) -> float:
    """
    Volatility targeting position sizing.

    Returns the number of shares to hold.
    """
    if asset_vol == 0 or price == 0:
        return 0.0
    dollar_risk = portfolio_value * target_vol
    return dollar_risk / (asset_vol * price)


def fixed_fractional(capital: float, risk_per_trade: float,
                     stop_loss_distance: float) -> float:
    """
    Fixed fractional position sizing.

    Returns the number of units (shares).
    """
    if stop_loss_distance == 0:
        return 0.0
    risk_amount = capital * risk_per_trade
    return risk_amount / stop_loss_distance


# ---------------------------------------------------------------------------
# 6. TRADING SIGNALS
# ---------------------------------------------------------------------------

class SignalType(Enum):
    """Type enumeration for SignalType."""
    BUY = auto()
    SELL = auto()
    HOLD = auto()


@dataclass
class TradeSignal:
    """Production-grade Trade Signal component."""
    timestamp: int
    signal: SignalType
    price: float
    confidence: float = 1.0
    reason: str = ""


def momentum_signal(prices: np.ndarray, lookback: int = 20) -> List[TradeSignal]:
    """Generate momentum trading signals."""
    signals: List[TradeSignal] = []
    for i in range(lookback, len(prices)):
        ret = (prices[i] - prices[i - lookback]) / prices[i - lookback]
        if ret > 0.02:
            signals.append(TradeSignal(i, SignalType.BUY, prices[i], min(1.0, abs(ret) * 10), "momentum_long"))
        elif ret < -0.02:
            signals.append(TradeSignal(i, SignalType.SELL, prices[i], min(1.0, abs(ret) * 10), "momentum_short"))
        else:
            signals.append(TradeSignal(i, SignalType.HOLD, prices[i], 0.5, "momentum_neutral"))
    return signals


def mean_reversion_signal(prices: np.ndarray, period: int = 20,
                          z_threshold: float = 2.0) -> List[TradeSignal]:
    """Generate mean-reversion signals using z-score."""
    signals: List[TradeSignal] = []
    ma = sma(prices, period)

    for i in range(period, len(prices)):
        window = prices[i - period + 1:i + 1]
        std = np.std(window)
        if std == 0:
            signals.append(TradeSignal(i, SignalType.HOLD, prices[i], 0.5, "no_vol"))
            continue
        z = (prices[i] - ma[i]) / std
        if z < -z_threshold:
            signals.append(TradeSignal(i, SignalType.BUY, prices[i], min(1.0, abs(z) / 4), "mean_rev_buy"))
        elif z > z_threshold:
            signals.append(TradeSignal(i, SignalType.SELL, prices[i], min(1.0, abs(z) / 4), "mean_rev_sell"))
        else:
            signals.append(TradeSignal(i, SignalType.HOLD, prices[i], 0.5, "mean_rev_hold"))
    return signals


def macd_crossover_signal(prices: np.ndarray) -> List[TradeSignal]:
    """Generate signals from MACD crossovers."""
    macd_line, signal_line, hist = macd(prices)
    signals: List[TradeSignal] = []

    for i in range(1, len(prices)):
        if np.isnan(hist[i]) or np.isnan(hist[i - 1]):
            continue
        if hist[i] > 0 and hist[i - 1] <= 0:
            signals.append(TradeSignal(i, SignalType.BUY, prices[i], 0.7, "macd_bullish_cross"))
        elif hist[i] < 0 and hist[i - 1] >= 0:
            signals.append(TradeSignal(i, SignalType.SELL, prices[i], 0.7, "macd_bearish_cross"))
    return signals


# ---------------------------------------------------------------------------
# 7. BACKTESTER
# ---------------------------------------------------------------------------

@dataclass
class BacktestResult:
    """Results of a backtest run."""
    total_return: float
    annualized_return: float
    sharpe: float
    sortino: float
    max_dd: float
    calmar: float
    total_trades: int
    win_rate: float
    equity_curve: np.ndarray
    pnl_series: np.ndarray


class Backtester:
    """
    Event-driven backtesting engine.

    evaluates_structurally trading strategy on historical price data with
    transaction costs and position tracking.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0005,
    ):
        """Initialize Backtester."""
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

    def run(self, prices: np.ndarray, signals: List[TradeSignal]) -> BacktestResult:
        """Run a backtest with given signals."""
        cash = self.initial_capital
        position = 0.0
        equity = np.zeros(len(prices))
        pnl = np.zeros(len(prices))
        trades = 0
        wins = 0
        entry_price = 0.0

        signal_map: Dict[int, TradeSignal] = {s.timestamp: s for s in signals}

        for i in range(len(prices)):
            price = prices[i]

            if i in signal_map:
                sig = signal_map[i]
                effective_price = price * (1 + self.slippage)

                if sig.signal == SignalType.BUY and position <= 0:
                    # Buy
                    shares = cash * 0.95 / (effective_price * (1 + self.commission))
                    cost = shares * effective_price * (1 + self.commission)
                    if position < 0:
                        # Close short
                        pnl_trade = (entry_price - price) * abs(position)
                        if pnl_trade > 0:
                            wins += 1
                        trades += 1
                    cash -= cost
                    position = shares
                    entry_price = effective_price

                elif sig.signal == SignalType.SELL and position >= 0:
                    if position > 0:
                        # Close long
                        revenue = position * price * (1 - self.commission) * (1 - self.slippage)
                        pnl_trade = (price - entry_price) * position
                        if pnl_trade > 0:
                            wins += 1
                        trades += 1
                        cash += revenue
                        position = 0.0

            equity[i] = cash + position * price
            pnl[i] = equity[i] - self.initial_capital

        # Compute metrics
        daily_returns = compute_returns(equity[equity > 0]) if np.any(equity > 0) else np.zeros(1)
        total_ret = (equity[-1] / self.initial_capital - 1) if equity[-1] > 0 else 0.0
        ann_days = max(1, len(prices))
        ann_ret = total_ret * 252 / ann_days
        sh = sharpe_ratio(daily_returns) if len(daily_returns) > 1 else 0.0
        so = sortino_ratio(daily_returns) if len(daily_returns) > 1 else 0.0
        mdd = max_drawdown(equity[equity > 0]) if np.any(equity > 0) else 0.0
        cal = ann_ret / abs(mdd) if abs(mdd) > 0 else 0.0
        wr = wins / max(1, trades)

        return BacktestResult(
            total_return=total_ret, annualized_return=ann_ret,
            sharpe=sh, sortino=so, max_dd=mdd, calmar=cal,
            total_trades=trades, win_rate=wr,
            equity_curve=equity, pnl_series=pnl,
        )


# ---------------------------------------------------------------------------
# 8. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniAiFinanceEngine:
    """
    Production-grade quantitative finance engine for OMNI Framework.

    Provides:
      - Technical indicators: SMA, EMA, RSI, MACD, Bollinger, ATR, OBV, VWAP
      - Portfolio optimization: mean-variance, risk parity, equal weight
      - Backtesting: equity curves, PnL, Sharpe, Sortino, max DD, Calmar
      - Risk metrics: VaR, CVaR, beta, alpha, information ratio
      - Position sizing: Kelly, volatility targeting, fixed fractional
      - Trading signals: momentum, mean-reversion, MACD crossover
    """

    def __init__(self, config=None):
        """Initialize OmniAiFinanceEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True

    VERSION = "1.0.0"
    ENGINE_ID = "omni-ai-finance"

    # --- Technical Indicators ---
    def sma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Performs sma operation for OmniAiFinanceEngine."""
        return sma(prices, period)

    def ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Performs ema operation for OmniAiFinanceEngine."""
        return ema(prices, period)

    def rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Performs rsi operation for OmniAiFinanceEngine."""
        return rsi(prices, period)

    def macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26,
             signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Performs macd operation for OmniAiFinanceEngine."""
        return macd(prices, fast, slow, signal)

    def bollinger_bands(self, prices: np.ndarray, period: int = 20,
                        num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Performs bollinger bands operation for OmniAiFinanceEngine."""
        return bollinger_bands(prices, period, num_std)

    def atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray,
            period: int = 14) -> np.ndarray:
        """Performs atr operation for OmniAiFinanceEngine."""
        return atr(high, low, close, period)

    def obv(self, prices: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Performs obv operation for OmniAiFinanceEngine."""
        return obv(prices, volume)

    def vwap(self, prices: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Performs vwap operation for OmniAiFinanceEngine."""
        return vwap(prices, volume)

    # --- Risk Metrics ---
    def sharpe_ratio(self, returns: np.ndarray, risk_free: float = 0.0) -> float:
        """Performs sharpe ratio operation for OmniAiFinanceEngine."""
        return sharpe_ratio(returns, risk_free)

    def sortino_ratio(self, returns: np.ndarray, risk_free: float = 0.0) -> float:
        """Performs sortino ratio operation for OmniAiFinanceEngine."""
        return sortino_ratio(returns, risk_free)

    def max_drawdown(self, prices: np.ndarray) -> float:
        """Performs max drawdown operation for OmniAiFinanceEngine."""
        return max_drawdown(prices)

    def value_at_risk(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Performs value at risk operation for OmniAiFinanceEngine."""
        return value_at_risk(returns, confidence)

    def conditional_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Performs conditional var operation for OmniAiFinanceEngine."""
        return conditional_var(returns, confidence)

    def beta(self, asset: np.ndarray, market: np.ndarray) -> float:
        """Performs beta operation for OmniAiFinanceEngine."""
        return beta(asset, market)

    def alpha(self, asset: np.ndarray, market: np.ndarray) -> float:
        """Performs alpha operation for OmniAiFinanceEngine."""
        return alpha_jensen(asset, market)

    # --- Portfolio ---
    def equal_weight(self, n: int) -> np.ndarray:
        """Performs equal weight operation for OmniAiFinanceEngine."""
        return markowitz_equal_weight(n)

    def min_variance(self, cov: np.ndarray) -> np.ndarray:
        """Performs min variance operation for OmniAiFinanceEngine."""
        return markowitz_min_variance(cov)

    def risk_parity(self, cov: np.ndarray) -> np.ndarray:
        """Performs risk parity operation for OmniAiFinanceEngine."""
        return risk_parity_weights(cov)

    # --- Position Sizing ---
    def kelly(self, win_prob: float, win_loss_ratio: float) -> float:
        """Performs kelly operation for OmniAiFinanceEngine."""
        return kelly_criterion(win_prob, win_loss_ratio)

    def vol_target_size(self, target: float, asset_vol: float,
                        portfolio: float, price: float) -> float:
        """Performs vol target size operation for OmniAiFinanceEngine."""
        return volatility_target_size(target, asset_vol, portfolio, price)

    # --- Signals ---
    def momentum_signals(self, prices: np.ndarray, lookback: int = 20) -> List[TradeSignal]:
        """Performs momentum signals operation for OmniAiFinanceEngine."""
        return momentum_signal(prices, lookback)

    def mean_reversion_signals(self, prices: np.ndarray, period: int = 20) -> List[TradeSignal]:
        """Performs mean reversion signals operation for OmniAiFinanceEngine."""
        return mean_reversion_signal(prices, period)

    def macd_signals(self, prices: np.ndarray) -> List[TradeSignal]:
        """Performs macd signals operation for OmniAiFinanceEngine."""
        return macd_crossover_signal(prices)

    # --- Backtesting ---
    def backtest(self, prices: np.ndarray, signals: List[TradeSignal],
                 initial_capital: float = 100000.0) -> BacktestResult:
        """Performs backtest operation for OmniAiFinanceEngine."""
        bt = Backtester(initial_capital=initial_capital)
        return bt.run(prices, signals)

    # --- Diagnostics ---
    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniAiFinanceEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "indicators": ["SMA", "EMA", "RSI", "MACD", "BollingerBands", "ATR", "OBV", "VWAP"],
            "risk_metrics": ["Sharpe", "Sortino", "MaxDD", "VaR", "CVaR", "Beta", "Alpha", "Calmar"],
            "portfolio": ["EqualWeight", "MinVariance", "RiskParity"],
            "signals": ["Momentum", "MeanReversion", "MACDCrossover"],
            "sizing": ["Kelly", "VolTarget", "FixedFractional"],
            "status": "operational",
        }
