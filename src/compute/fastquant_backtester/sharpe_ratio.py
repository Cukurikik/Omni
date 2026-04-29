class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class QuantMath:
    def __init__(self):
        pass

    def compute_sharpe_ratio(self, strategy_returns: list[float], risk_free_rate: float) -> OmniResult:
        if not strategy_returns:
            return OmniResult(error="Returns array cannot be empty")

        # Deterministic simulation of Annualized Sharpe Ratio
        try:
            n = len(strategy_returns)
            if n < 2:
                return OmniResult(error="Need at least 2 return periods to calculate standard deviation")
                
            # Mean return
            mean_return = sum(strategy_returns) / n
            
            # Excess return
            excess_return = mean_return - risk_free_rate
            
            # Standard Deviation (Volatility)
            variance = sum((r - mean_return) ** 2 for r in strategy_returns) / (n - 1)
            volatility = variance ** 0.5
            
            if volatility == 0.0:
                return OmniResult(value=0.0)
                
            # Annualize (assuming daily returns: 252 trading days)
            annualized_sharpe = (excess_return / volatility) * (252 ** 0.5)
            
            return OmniResult(value=annualized_sharpe)
        except Exception as e:
            return OmniResult(error=str(e))
