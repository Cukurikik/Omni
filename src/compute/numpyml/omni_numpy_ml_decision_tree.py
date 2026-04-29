# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Numpy-ML Decision Tree (OMNI Zero-Mock Implementation)
# Implements Gini Impurity metric for CART splits.

from dataclasses import dataclass
from typing import List, Optional

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

class NumpyMLCART:
    def _calculate_gini(self, y: List[int]) -> float:
        if not y:
            return 0.0
            
        counts = {}
        for label in y:
            counts[label] = counts.get(label, 0) + 1
            
        impurity = 1.0
        n_instances = float(len(y))
        for count in counts.values():
            prob = count / n_instances
            impurity -= (prob * prob)
            
        return impurity

    def split_evaluation(self, y_left: List[int], y_right: List[int]) -> Result:
        n_left = len(y_left)
        n_right = len(y_right)
        total = n_left + n_right
        
        if total == 0:
            return Result.err("Split subset is entirely empty.")

        p_left = n_left / total
        p_right = n_right / total
        
        # Gini Index metric
        gini_left = self._calculate_gini(y_left)
        gini_right = self._calculate_gini(y_right)
        
        weighted_impurity = (p_left * gini_left) + (p_right * gini_right)
        
        return Result.ok(weighted_impurity)
