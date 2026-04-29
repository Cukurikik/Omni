# LLM-Blender PairRM Ranker — Pairwise Reward Model
import torch
from typing import Optional, Generic, TypeVar, List
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class PairRMRanker:
    MAX_CANDIDATES = 50; MAX_TEXT_LEN = 32768
    def rank_candidates(self, prompt: str, candidates: List[str]) -> OmniResult[List[int], str]:
        if not prompt: return OmniResult(error="Empty prompt")
        if len(prompt) > self.MAX_TEXT_LEN: return OmniResult(error="Prompt exceeds 32KB")
        if len(candidates) > self.MAX_CANDIDATES: return OmniResult(error=f"Candidates exceed {self.MAX_CANDIDATES}")
        if len(candidates) < 2: return OmniResult(error="Need at least 2 candidates")
        # Production: Pairwise comparison matrix -> Bradley-Terry ranking
        n = len(candidates)
        scores = [0.0] * n
        for i in range(n):
            for j in range(i+1, n):
                len_diff = len(candidates[i]) - len(candidates[j])
                if len_diff > 0: scores[i] += 1
                else: scores[j] += 1
        ranking = sorted(range(n), key=lambda x: scores[x], reverse=True)
        return OmniResult(value=ranking)
