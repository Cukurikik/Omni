"""
OMNI MOTHER - Semester 12, Batch 20
Engine: OmniAdEMAMixEngine
AdEMAMix: Dual EMA Optimizer (nanowell/AdEMAMix-Optimizer-Pytorch).

Implements the full AdEMAMix optimizer algorithm:
  - Dual exponential moving averages (fast β1, slow β3)
  - Bias-corrected second moment (Adam-style v_t)
  - Mixed momentum update rule
  - Training trajectory computation with loss tracking
  - Convergence analysis metrics

Architecture: Production-grade, zero-mock, monadic Result[T, E]
"""
import math
import numpy as np

class Ok:
    def __init__(self, v): self.value = v
    def is_ok(self): return True
    def is_err(self): return False
class Err:
    def __init__(self, e): self.error = e
    def is_ok(self): return False
    def is_err(self): return True

class OmniAdEMAMixEngine:
    """AdEMAMix: Adaptive EMA Mixture optimizer with dual momentum."""
    def __init__(self):
        self.engine_id = "OmniAdEMAMixEngine"
        self.version = "1.0.0"
        self.batch = 20
        self.semester = 12
        self.beta1 = 0.9       # fast EMA
        self.beta2 = 0.999     # second moment
        self.beta3 = 0.9999    # slow EMA
        self.alpha_mix = 0.1   # mixing weight for slow EMA
        self.lr = 0.001
        self.eps = 1e-8
        self.n_params = 32

    def _step(self, params, grad, m_fast, m_slow, v, t):
        """Single AdEMAMix optimizer step."""
        # Fast EMA
        m_fast = self.beta1 * m_fast + (1 - self.beta1) * grad
        # Slow EMA
        m_slow = self.beta3 * m_slow + (1 - self.beta3) * grad
        # Second moment
        v = self.beta2 * v + (1 - self.beta2) * (grad ** 2)
        # Bias correction
        m_fast_hat = m_fast / (1 - self.beta1 ** t)
        m_slow_hat = m_slow / (1 - self.beta3 ** t)
        v_hat = v / (1 - self.beta2 ** t)
        # Mixed momentum
        m_mixed = (1 - self.alpha_mix) * m_fast_hat + self.alpha_mix * m_slow_hat
        # Update
        params = params - self.lr * m_mixed / (np.sqrt(v_hat) + self.eps)
        return params, m_fast, m_slow, v

    def _rosenbrock_loss(self, params):
        """Rosenbrock function as a test loss landscape."""
        loss = 0.0
        for i in range(len(params) - 1):
            loss += 100 * (params[i + 1] - params[i] ** 2) ** 2 + (1 - params[i]) ** 2
        return float(loss)

    def _rosenbrock_grad(self, params):
        """Analytical gradient of Rosenbrock."""
        grad = np.zeros_like(params)
        for i in range(len(params) - 1):
            grad[i] += -400 * params[i] * (params[i + 1] - params[i] ** 2) - 2 * (1 - params[i])
            grad[i + 1] += 200 * (params[i + 1] - params[i] ** 2)
        return grad

    def process(self, payload: dict):
        try:
            rng = np.random.RandomState(42)
            n_steps = payload.get('n_steps', 50)
            init_params = np.array(payload.get('init_params', rng.randn(self.n_params).tolist()), dtype=np.float64)
            params = init_params.copy()
            m_fast = np.zeros_like(params)
            m_slow = np.zeros_like(params)
            v = np.zeros_like(params)
            losses = []
            for t in range(1, n_steps + 1):
                grad = self._rosenbrock_grad(params)
                loss = self._rosenbrock_loss(params)
                losses.append(loss)
                params, m_fast, m_slow, v = self._step(params, grad, m_fast, m_slow, v, t)
            final_loss = self._rosenbrock_loss(params)
            losses.append(final_loss)
            # Convergence analysis
            loss_reduction = losses[0] - final_loss
            converged = final_loss < losses[0] * 0.1
            result = {
                'initial_loss': losses[0],
                'final_loss': final_loss,
                'loss_reduction': loss_reduction,
                'converged': converged,
                'n_steps': n_steps,
                'loss_trajectory': [losses[i] for i in range(0, len(losses), max(1, len(losses) // 10))],
                'param_norm': float(np.linalg.norm(params)),
                'fast_ema_norm': float(np.linalg.norm(m_fast)),
                'slow_ema_norm': float(np.linalg.norm(m_slow)),
            }
            return Ok(result)
        except Exception as e:
            return Err(f"{self.engine_id} error: {str(e)}")

    def diagnostics(self) -> dict:
        return {'engine_id': self.engine_id, 'version': self.version, 'batch': self.batch, 'semester': self.semester, 'status': 'operational', 'beta1': self.beta1, 'beta3': self.beta3}
