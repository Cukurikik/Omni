# Qwen2.5-Math — Mathematical Reasoning Verifier
import math, re
from typing import Optional, Generic, TypeVar, List
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class MathVerifier:
    MAX_EXPR_LEN = 10000
    def verify_numerical(self, predicted: str, ground_truth: str, tolerance: float = 1e-6) -> OmniResult[bool, str]:
        if not predicted or not ground_truth: return OmniResult(error="Empty input")
        if len(predicted) > self.MAX_EXPR_LEN: return OmniResult(error="Expression too long")
        try:
            p = float(predicted.strip().replace(",", ""))
            g = float(ground_truth.strip().replace(",", ""))
            if math.isnan(p) or math.isnan(g): return OmniResult(error="NaN detected")
            return OmniResult(value=abs(p - g) <= tolerance)
        except ValueError:
            return OmniResult(value=predicted.strip() == ground_truth.strip())

    def extract_boxed_answer(self, solution: str) -> OmniResult[str, str]:
        if not solution: return OmniResult(error="Empty solution")
        pattern = r'\\boxed\{([^}]+)\}'
        matches = re.findall(pattern, solution)
        if not matches: return OmniResult(error="No \\boxed{} found")
        return OmniResult(value=matches[-1].strip())
