class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class VolatilityLP:
    def __init__(self):
        pass

    def compute_optimal_bid(self, current_price: float, volatility_index: float, baseline_on_demand_price: float) -> OmniResult:
        if current_price < 0 or volatility_index < 0 or baseline_on_demand_price <= 0:
            return OmniResult(error="Pricing metrics must be positive")

        # Deterministic calculation of Spot Instance Pricing Arbitrage
        # Uses Linear Programming heuristics to bid for cheap interrupted cloud compute (e.g. AWS EC2 Spot)
        try:
            if current_price >= baseline_on_demand_price * 0.8:
                # If spot price is 80% or more of on-demand, the arbitrage is dead. Don't bid.
                return OmniResult(value={"bid_price": 0.0, "should_bid": False})
                
            # If volatility is high, we must bid slightly above market to survive the termination wave
            bid_multiplier = 1.0 + (volatility_index * 0.1)
            calculated_bid = current_price * bid_multiplier
            
            # Cap the bid to 50% of the on-demand price
            final_bid = min(calculated_bid, baseline_on_demand_price * 0.5)
            
            return OmniResult(value={"bid_price": final_bid, "should_bid": True})
        except Exception as e:
            return OmniResult(error=str(e))
