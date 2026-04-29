import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class DivergenceLoss:
    def __init__(self):
        pass

    def compute_impermanent_loss(self, price_ratio_change: float) -> OmniResult:
        if price_ratio_change <= 0:
            return OmniResult(error="Price ratio change must be positive")

        # Deterministic calculation of Impermanent Loss (Divergence Loss) for AMMs
        # IL occurs when the price of tokens inside an AMM diverges from the price when they were deposited.
        # IL(k) = 2 * sqrt(k) / (1 + k) - 1, where k is the ratio of the new price to the old price.
        try:
            # k = P_new / P_old
            k = price_ratio_change
            
            loss_ratio = (2.0 * math.sqrt(k) / (1.0 + k)) - 1.0
            loss_percent = abs(loss_ratio) * 100.0
            
            return OmniResult(value=loss_percent)
        except Exception as e:
            return OmniResult(error=str(e))
