import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class PoissonArrivalModel:
    def __init__(self):
        pass

    def compute_cold_start_probability(self, lambda_rate: float, time_window_seconds: float) -> OmniResult:
        if lambda_rate < 0 or time_window_seconds <= 0:
            return OmniResult(error="Invalid Poisson parameters")

        # Deterministic calculation of Poisson probability for Serverless arrivals
        # Predicts if a serverless function needs to be pre-warmed to avoid cold starts
        try:
            # Expected events in time window (lambda * t)
            expected_events = lambda_rate * time_window_seconds
            
            # Probability of EXACTLY 0 events happening in this time window: P(X=0) = e^(-lambda*t)
            prob_zero = math.exp(-expected_events)
            
            # Probability of at least 1 event (requiring the function to be warm)
            prob_active = 1.0 - prob_zero
            
            return OmniResult(value=prob_active)
        except Exception as e:
            return OmniResult(error=str(e))
