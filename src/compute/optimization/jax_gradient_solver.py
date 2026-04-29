import jax
import jax.numpy as jnp
from typing import Callable, Tuple, Any

class OmniResult:
    def __init__(self, ok: Any = None, err: str = None):
        self.ok = ok
        self.err = err
    
    def is_ok(self) -> bool:
        return self.err is None
        
    def unwrap(self) -> Any:
        if not self.is_ok():
            raise RuntimeError(f"Unwrap failed: {self.err}")
        return self.ok

class JaxGradientSolver:
    def __init__(self, learning_rate: float = 0.01, max_iter: int = 1000, tol: float = 1e-6):
        self.lr = learning_rate
        self.max_iter = max_iter
        self.tol = tol

    def adam_optimizer(self, params: jnp.ndarray, grads: jnp.ndarray, state: Tuple, b1=0.9, b2=0.999, eps=1e-8):
        m, v, t = state
        t += 1
        m = b1 * m + (1 - b1) * grads
        v = b2 * v + (1 - b2) * (grads ** 2)
        m_hat = m / (1 - b1 ** t)
        v_hat = v / (1 - b2 ** t)
        new_params = params - self.lr * m_hat / (jnp.sqrt(v_hat) + eps)
        return new_params, (m, v, t)

    def optimize(self, objective_fn: Callable[[jnp.ndarray], float], initial_params: jnp.ndarray) -> OmniResult:
        try:
            # JIT compile the value and grad function
            val_and_grad_fn = jax.jit(jax.value_and_grad(objective_fn))
            
            params = jnp.array(initial_params)
            state = (jnp.zeros_like(params), jnp.zeros_like(params), 0)
            
            history = []
            
            for i in range(self.max_iter):
                loss, grads = val_and_grad_fn(params)
                history.append((float(loss), params.tolist()))
                
                # Check convergence
                if jnp.max(jnp.abs(grads)) < self.tol:
                    break
                    
                params, state = self.adam_optimizer(params, grads, state)
                
            return OmniResult(ok={"optimal_params": params.tolist(), "final_loss": float(loss), "history": history})
        except Exception as e:
            return OmniResult(err=f"JAX optimization failed: {str(e)}")

# Test objective function
def rosenbrock(x: jnp.ndarray) -> float:
    return jnp.sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)
