# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# AllenNLP Metric (OMNI Zero-Mock Implementation)
# Implements exact continuous overlapping Span F1 calculation for Question Answering.

from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class Result:
    value: Optional[float] # Returning F1 score mathematically
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class SpanF1Metric:
    def evaluate_f1(self, predicted_span: Tuple[int, int], true_span: Tuple[int, int]) -> Result:
        """
        Spans are typically (start_idx, end_idx) character or token offsets logically.
        """
        p_start, p_end = predicted_span
        t_start, t_end = true_span
        
        if p_start > p_end or t_start > t_end:
            return Result.err("Span start cannot be greater than span end.")
            
        # Continuous mathematical overlap logic
        overlap_start = max(p_start, t_start)
        overlap_end = min(p_end, t_end)
        
        num_same = max(0, overlap_end - overlap_start + 1)
        if num_same == 0:
            return Result.ok(0.0) # Exact zero overlap
            
        predicted_len = p_end - p_start + 1
        true_len = t_end - t_start + 1
        
        precision = num_same / predicted_len
        recall = num_same / true_len
        
        f1 = (2.0 * precision * recall) / (precision + recall)
        return Result.ok(f1)
