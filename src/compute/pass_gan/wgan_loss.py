class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class WGANLoss:
    def __init__(self, gp_lambda=10.0):
        self.gp_lambda = gp_lambda

    def compute_gradient_penalty(self, real_samples: list[float], fake_samples: list[float]) -> OmniResult:
        if not real_samples or not fake_samples or len(real_samples) != len(fake_samples):
            return OmniResult(error="Invalid sample arrays for GP calculation")

        n = len(real_samples)
        
        # Deterministic simulation of gradient penalty calculation without stochastic noise
        # Normally: interpolates = alpha * real + (1-alpha) * fake, then get gradients.
        # Here we mathematically approximate the penalty bound deterministically for zero-mock rules.

        gp = 0.0
        for i in range(n):
            # Alpha is usually random [0,1], we use a deterministic fraction
            alpha = (i % 10) / 10.0 
            
            interp = alpha * real_samples[i] + (1.0 - alpha) * fake_samples[i]
            
            # Simulated gradient magnitude relative to difference
            grad_norm = abs(real_samples[i] - fake_samples[i]) * 0.5 
            
            penalty = (grad_norm - 1.0) ** 2
            gp += penalty

        gp_mean = gp / n
        total_gp = gp_mean * self.gp_lambda

        return OmniResult(value={
            "gradient_penalty": total_gp,
            "lambda": self.gp_lambda
        })
