import numpy as np
from typing import Dict, Any, List
from dataclasses import dataclass

# OMNI MMIQ Eval Engine
# Computational Layer
# Multi-Modal Intelligence Quality numerical scoring. Evaluates mathematical bounds without API mockers.

@dataclass
class EvalResult:
    ok: bool
    final_score: float = 0.0
    sub_scores: Dict[str, float] = None
    error: str = None

class OmniMmiqEvalEngine:
    def __init__(self, strictness_penalty: float = 0.1):
        self.penalty = strictness_penalty
        self.evaluations = 0

    def calculate_quality_metric(self, alignment_matrix: np.ndarray, response_entropy: np.ndarray) -> EvalResult:
        """
        Determines answer quality strictly via vector calculations. No LLM "as a judge" mock loop.
        alignment_matrix: Shape (N, M) representing cosine similarities between image regions and text tokens.
        response_entropy: Shape (M,) representing Shannon entropy of text token generation.
        """
        if not isinstance(alignment_matrix, np.ndarray) or not isinstance(response_entropy, np.ndarray):
            return EvalResult(False, error="MMIQ: Inputs must be numpy arrays")
            
        if alignment_matrix.ndim != 2 or response_entropy.ndim != 1:
            return EvalResult(False, error="MMIQ: Alignment must be 2D, entropy must be 1D")
            
        if alignment_matrix.shape[1] != response_entropy.shape[0]:
            return EvalResult(False, error="MMIQ: Dimension mismatch between alignment and entropy")

        try:
            self.evaluations += 1
            
            # Sub-score 1: Modality Alignment Strength (MAS)
            # Calculated as the mean of the maximum semantic correlations 
            max_alignments = np.max(alignment_matrix, axis=0)
            mas = float(np.mean(max_alignments))
            
            # Sub-score 2: Certainty Score (CS)
            # Entropy indicates uncertainty. Lower entropy = higher certainty.
            # Normalize entropy assumption max ~ 10.0 (approx LN(vocab))
            avg_entropy = float(np.mean(response_entropy))
            cs = max(0.0, 1.0 - (avg_entropy / 10.0))
            
            # Sub-score 3: Visual Hallucination Penalty (VHP)
            # If tokens have low max visual alignment but high certainty, it's hallucinating visually.
            hallucination_delta = np.maximum(0.0, (1.0 - max_alignments) - (response_entropy / 10.0))
            vhp_penalty = float(np.mean(hallucination_delta)) * self.penalty * 10.0
            
            # Final MMIQ numerical composition
            final_mmiq = (mas * 0.6) + (cs * 0.4) - vhp_penalty
            final_mmiq = max(0.0, min(1.0, final_mmiq)) # Clamp 0-1
            
            sub_scores = {
                "Modality_Alignment_Strength": mas,
                "Certainty_Score": cs,
                "Visual_Hallucination_Penalty": vhp_penalty
            }
            
            return EvalResult(True, final_score=final_mmiq, sub_scores=sub_scores)
            
        except Exception as e:
            return EvalResult(False, error=f"MMIQ: Numerical constraint violation: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMmiqEvalEngine",
            "evals_run": self.evaluations,
            "strictness_penalty": self.penalty,
            "status": "Operational"
        }
