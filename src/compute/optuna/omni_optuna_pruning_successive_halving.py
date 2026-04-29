# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Optuna Pruning (OMNI Zero-Mock Implementation)
# Implements Successive Halving mathematical early elimination algorithm.

from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Result:
    value: Optional[List[int]] # Indices of trials to KEEP
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[int]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class SuccessiveHalvingPruner:
    def prune_trials(self, trial_scores: List[float], reduction_factor: int) -> Result:
        """
        Takes a list of trial scores. Lower is better. 
        Promotes only the top 1/reduction_factor of the trials mathematically.
        """
        if not trial_scores:
             return Result.err("Trial scores list cannot be empty.")
             
        if reduction_factor <= 1:
             return Result.err("Reduction factor must be > 1 to prune.")
             
        num_trials = len(trial_scores)
        keep_count = num_trials // reduction_factor
        
        if keep_count == 0 and num_trials > 0:
             keep_count = 1 # Always keep at least 1
             
        # Associate idx to keep track
        indexed_scores = [(idx, score) for idx, score in enumerate(trial_scores)]
        
        # Sort ascending (lower score is better objective)
        indexed_scores.sort(key=lambda x: x[1])
        
        keep_indices = [idx for idx, _ in indexed_scores[:keep_count]]
        return Result.ok(keep_indices)
