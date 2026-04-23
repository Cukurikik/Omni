"""OmniCustomStackCalculatorEngine implementing a robust RPN evaluator."""
from typing import Dict, Any, List, Union
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniCustomStackCalculatorEngine(OmniBaseEngine):
    """Production-grade Omni Custom Stack Calculator Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def evaluate_rpn(self, tokens: List[Union[int, float, str]]) -> Result[float, str]:
        """
        Evaluates a Reverse Polish Notation (RPN) expression.
        Supported operators: +, -, *, /, %
        """
        try:
            stack: List[float] = []

            for token in tokens:
                if isinstance(token, (int, float)):
                    stack.append(float(token))
                elif isinstance(token, str):
                    try:
                        val = float(token)
                        stack.append(val)
                    except ValueError:
                        # Must be an operator
                        if len(stack) < 2:
                            return Result.fail(f"Insufficient operands for operator '{token}'")
                        
                        b = stack.pop()
                        a = stack.pop()
                        
                        if token == '+':
                            stack.append(a + b)
                        elif token == '-':
                            stack.append(a - b)
                        elif token == '*':
                            stack.append(a * b)
                        elif token == '/':
                            if b == 0:
                                return Result.fail("Division by zero")
                            stack.append(a / b)
                        elif token == '%':
                            if b == 0:
                                return Result.fail("Modulo by zero")
                            stack.append(a % b)
                        else:
                            return Result.fail(f"Unknown operator '{token}'")

            if len(stack) != 1:
                return Result.fail(f"Invalid expression: {len(stack)} items left on stack")

            return Result.ok(stack[0])
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniCustomStackCalculatorEngine",
            "status": "operational",
            "type": "Reverse Polish Notation Evaluation"
        }
