"from typing import List\
\
class SymSolverRPN:\
    def evaluate_rpn(self, tokens: List[str]) -> float:\
        stack = []\
        for token in tokens:\
            if token in [\"+\", \"-\", \"*\", \"/\"]:\
                if len(stack) < 2:\
         
<truncated 544 bytes>