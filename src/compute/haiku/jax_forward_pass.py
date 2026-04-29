import jax
import jax.numpy as jnp
import haiku as hk
from typing import Any, Tuple, Dict

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class HaikuForwardPass:
    def __init__(self, hidden_sizes=(128, 64, 10)):
        self.hidden_sizes = hidden_sizes
        
        def _forward(x):
            mlp = hk.nets.MLP(self.hidden_sizes)
            return mlp(x)
            
        self.network = hk.transform(_forward)
        self.rng_key = jax.random.PRNGKey(42)

    def init_params(self, sample_input: jnp.ndarray) -> OmniResult:
        try:
            params = self.network.init(self.rng_key, sample_input)
            return OmniResult.ok(params)
        except Exception as e:
            return OmniResult.err(f"Haiku initialization failed: {str(e)}")

    def forward(self, params: hk.Params, inputs: jnp.ndarray) -> OmniResult:
        try:
            # JIT compiled forward pass
            @jax.jit
            def _apply(p, x):
                return self.network.apply(p, self.rng_key, x)
                
            output = _apply(params, inputs)
            return OmniResult.ok(output)
        except Exception as e:
            return OmniResult.err(f"Haiku forward pass failed: {str(e)}")
