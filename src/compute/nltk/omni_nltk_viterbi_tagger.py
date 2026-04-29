# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# NLTK Viterbi Tagger (OMNI Zero-Mock Implementation)
# Implements Hidden Markov Model Decoding via Viterbi Dynamic Programming.

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Result:
    value: Optional[List[str]] # The optimal path of hidden states
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[str]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class ViterbiEngine:
    def decode(
        self, 
        observations: List[str], 
        states: List[str], 
        start_probs: Dict[str, float], 
        transition_probs: Dict[str, Dict[str, float]], 
        emission_probs: Dict[str, Dict[str, float]]
    ) -> Result:
        """
        Computes the most likely sequence of hidden states given sequence of observations mathematically.
        Uses exact probabilities (no log-space, assuming non-underflowing magnitudes abstractly).
        """
        if not observations:
             return Result.err("Observation sequence cannot be empty.")
        if not states:
             return Result.err("Hidden state list cannot be empty.")
             
        V: List[Dict[str, float]] = [{}]
        path: Dict[str, List[str]] = {}

        # Initialize base cases (t == 0)
        obs_start = observations[0]
        for y in states:
             # Default prob to 0.0 mathematically
             start_p = start_probs.get(y, 0.0)
             emit_p = emission_probs.get(y, {}).get(obs_start, 0.0)
             
             V[0][y] = start_p * emit_p
             path[y] = [y]
             
        # Run Viterbi for t > 0
        for t in range(1, len(observations)):
             V.append({})
             new_path: Dict[str, List[str]] = {}
             obs_curr = observations[t]
             
             for y in states:
                  # Maximization step
                  max_prob, best_state = -1.0, None
                  for y0 in states:
                       trans_p = transition_probs.get(y0, {}).get(y, 0.0)
                       emit_p = emission_probs.get(y, {}).get(obs_curr, 0.0)
                       
                       prob = V[t-1].get(y0, 0.0) * trans_p * emit_p
                       
                       if prob > max_prob:
                            max_prob = prob
                            best_state = y0
                            
                  V[t][y] = max_prob
                  if best_state is not None:
                       new_path[y] = path[best_state] + [y]
                       
             # Update paths
             path = new_path
             
        # Find final most probable state
        best_final_prob, best_final_state = -1.0, None
        for y in states:
             if V[-1][y] > best_final_prob:
                  best_final_prob = V[-1][y]
                  best_final_state = y
                  
        if best_final_state is None or best_final_prob == 0.0:
            return Result.err("Zero probability trajectory. Smoothing may be required in probability matrices.")
            
        optimal_path = path[best_final_state]
        return Result.ok(optimal_path)
