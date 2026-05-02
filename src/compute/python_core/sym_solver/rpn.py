"""
@omni-domain Compute Layer (Symbolic Solver)
@omni-source sym-math
@omni-description Reverse Polish Notation Evaluator.
@omni-requirement zero-mock, monadic-error
"""
from typing import List, Any, Optional
import math

class OmniResult:
    def __init__(self, ok: bool, value: Any = None, err: Optional[Exception] = None):
        self.ok = ok
        self.value = value
        self.err = err

    @staticmethod
    def ok(value: Any) -> 'OmniResult':
        return OmniResult(True, value=value)

    @staticmethod
    def err(err: Exception) -> 'OmniResult':
        return OmniResult(False, err=err)

class RPNSolver:
    def evaluate(self, tokens: List[str]) -> OmniResult:
        if not tokens:
            return OmniResult.err(ValueError("Empty tokens"))
            
        stack = []
        try:
            for token in tokens:
                if token in ('+', '-', '*', '/'):
                    if len(stack) < 2:
                        return OmniResult.err(ValueError("Insufficient operands"))
                    b = stack.pop()
                    a = stack.pop()
                    if token == '+': stack.append(a + b)
                    elif token == '-': stack.append(a - b)
                    elif token == '*': stack.append(a * b)
                    elif token == '/': 
                        if b == 0: return OmniResult.err(ZeroDivisionError("Division by zero"))
                        stack.append(a / b)
                else:
                    stack.append(float(token))
            
            if len(stack) != 1:
                return OmniResult.err(ValueError("Invalid expression"))
            return OmniResult.ok(stack[0])
        except Exception as e:
            return OmniResult.err(e)