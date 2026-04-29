import math
from scipy.stats import norm

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class PdeSolver:
    def __init__(self):
        pass

    def compute_call_option_price(self, spot_price: float, strike_price: float, time_to_maturity_years: float, risk_free_rate: float, volatility: float) -> OmniResult:
        if spot_price <= 0 or strike_price <= 0 or time_to_maturity_years <= 0 or volatility <= 0:
            return OmniResult(error="Prices, time, and volatility must be positive")

        # Deterministic calculation of the Black-Scholes-Merton Options Pricing Formula
        # Solves the Partial Differential Equation (PDE) for a European Call Option.
        try:
            d1 = (math.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity_years) / (volatility * math.sqrt(time_to_maturity_years))
            d2 = d1 - volatility * math.sqrt(time_to_maturity_years)
            
            call_price = (spot_price * norm.cdf(d1)) - (strike_price * math.exp(-risk_free_rate * time_to_maturity_years) * norm.cdf(d2))
            
            return OmniResult(value=call_price)
        except Exception as e:
            return OmniResult(error=str(e))
