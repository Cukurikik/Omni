import math

class BleuEvaluator:
    def brevity_penalty(self, c: int, r: int) -> float:
        if c > r:
            return 1.0
        elif c == 0:
            return 0.0
        else:
            return math.exp(1 - (r / c))
