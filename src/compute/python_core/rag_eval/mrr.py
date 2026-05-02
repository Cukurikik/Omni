"""
@omni-domain Compute Layer (RAG Evaluation)
@omni-source rag-eval-toolkit
@omni-description Mean Reciprocal Rank (MRR) engine for RAG system evaluation.
@omni-requirement zero-mock, monadic-error
"""
from typing import List, Any, Optional

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

class RAGEvaluatorMRR:
    def compute_mrr(self, rank_positions: List[int]) -> OmniResult:
        if not rank_positions:
            return OmniResult.err(ValueError("Rank positions list cannot be empty"))
        
        try:
            score = sum(1.0 / r for r in rank_positions if r > 0)
            mrr = score / len(rank_positions)
            return OmniResult.ok(mrr)
        except Exception as e:
            return OmniResult.err(e)
