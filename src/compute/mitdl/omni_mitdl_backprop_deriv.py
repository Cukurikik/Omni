# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# MIT Deep Learning Book Derivation (OMNI Zero-Mock Implementation)
# Implements mathematical derivative chain abstraction for scalar variables.

from dataclasses import dataclass
from typing import Optional

@dataclass
class Result:
    value: Optional[float]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AutomaticDerivation:
    def _power_rule(self, base: float, exponent: float) -> float:
        # dx^n = n * x^(n-1)
        if base == 0 and exponent < 1:
            return 0.0 # Guard zero div
        return exponent * (base ** (exponent - 1.0))
        
    def _relu_derivative(self, x: float) -> float:
        return 1.0 if x > 0 else 0.0

    def compute_chain_rule(self, f_vals: list[float], f_types: list[str]) -> Result:
        """
        f_types: ['linear', 'relu', 'power_2']
        Evaluates df / dx by multiplying local gradients in chain sequence.
        """
        if len(f_vals) != len(f_types):
             return Result.err("Derivative chain sequence mismatch.")
             
        global_gradient = 1.0
        
        for val, ftype in zip(f_vals, f_types):
            local_grad = 0.0
            if ftype == 'linear':
                local_grad = 1.0
            elif ftype == 'relu':
                local_grad = self._relu_derivative(val)
            elif ftype == 'power_2':
                local_grad = self._power_rule(val, 2.0)
            else:
                return Result.err(f"Unsupported activation abstraction: {ftype}")
                
            global_gradient *= local_grad
            
        return Result.ok(global_gradient)
