"""OmniShuntingYardEngine for math expression evaluation."""
from typing import Dict, Any, List
import operator
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniShuntingYardEngine(OmniBaseEngine):
    """Production-grade Omni Shunting Yard Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self):
        self.ops = {
            '+': (1, operator.add),
            '-': (1, operator.sub),
            '*': (2, operator.mul),
            '/': (2, operator.truediv),
            '^': (3, operator.pow)
        }

    def evaluate(self, expression: str) -> Result[Dict[str, Any], str]:
        """Evaluates an infix mathematical expression."""
        try:
            tokens = self._tokenize(expression)
            rpn = self._to_rpn(tokens)
            res = self._eval_rpn(rpn)
            return Result.ok({"rpn": rpn, "result": res})
        except Exception as e:
            return Result.fail(str(e))

    def _tokenize(self, expr: str) -> List[str]:
        tokens = []
        curr = ""
        for c in expr:
            if c.isspace():
                if curr:
                    tokens.append(curr)
                    curr = ""
            elif c in self.ops or c in ['(', ')']:
                if curr:
                    tokens.append(curr)
                    curr = ""
                tokens.append(c)
            else:
                curr += c
        if curr:
            tokens.append(curr)
        return tokens

    def _to_rpn(self, tokens: List[str]) -> List[str]:
        out = []
        stack = []
        for tok in tokens:
            if tok.replace('.', '', 1).isdigit():
                out.append(tok)
            elif tok in self.ops:
                while stack and stack[-1] != '(' and self.ops[stack[-1]][0] >= self.ops[tok][0]:
                    out.append(stack.pop())
                stack.append(tok)
            elif tok == '(':
                stack.append(tok)
            elif tok == ')':
                while stack and stack[-1] != '(':
                    out.append(stack.pop())
                if stack and stack[-1] == '(':
                    stack.pop()
        while stack:
            out.append(stack.pop())
            
        return out

    def _eval_rpn(self, rpn: List[str]) -> float:
        stack = []
        for tok in rpn:
            if tok in self.ops:
                b = stack.pop()
                a = stack.pop()
                stack.append(self.ops[tok][1](a, b))
            else:
                stack.append(float(tok))
        return stack[0] if stack else 0.0

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniShuntingYardEngine",
            "status": "operational",
            "supported_ops": list(self.ops.keys())
        }
