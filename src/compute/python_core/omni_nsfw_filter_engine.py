"""
OMNI NSFW Filter Engine
=======================
Production-grade OMNI engine mathematically formatting NLP CV mappings
into strict safety moderation thresholds. Inspired by GantMan/nsfw_model.

Features:
- Deterministic gating probabilities across discrete explicit classes.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Union

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"


class NsfwFilterErr(Exception):
    pass


@dataclass(frozen=True)
class Ok:
    value: Any


@dataclass(frozen=True)
class Err:
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. PROBABILITY GATING MATH
# ---------------------------------------------------------------------------

class ThresholdGatekeeper:
    """Implement exact routing gating predictions into Moderation Boolean states."""
    
    # Pre-defined known categorical clusters
    EXPLICIT_CLASSES = {"porn", "hentai"}
    SENSITIVE_CLASSES = {"sexy"}
    SAFE_CLASSES = {"neutral", "drawings"}

    @staticmethod
    def evaluate_safety(prob_map: Dict[str, float], explicit_thres: float, sensitive_thres: float) -> Dict[str, Any]:
        """Calculates discrete moderation status from continuous probability fields."""
        
        # Pull highest confidence explicit markers
        exp_score = sum(prob_map.get(k, 0.0) for k in ThresholdGatekeeper.EXPLICIT_CLASSES)
        sen_score = sum(prob_map.get(k, 0.0) for k in ThresholdGatekeeper.SENSITIVE_CLASSES)
        safe_score = sum(prob_map.get(k, 0.0) for k in ThresholdGatekeeper.SAFE_CLASSES)
        
        # Primary gating trigger
        if exp_score >= explicit_thres:
            verdict = "REJECTED_EXPLICIT"
            highest_risk = "explicit_content"
        elif sen_score >= sensitive_thres:
            verdict = "FLAGGED_REVIEW"
            highest_risk = "suggestive_content"
        else:
            verdict = "PASSED_SAFE"
            highest_risk = "none"

        return {
            "verdict": verdict,
            "primary_risk_flag": highest_risk,
            "calculated_explicit_sum": exp_score,
            "calculated_sensitive_sum": sen_score,
            "safety_confidence": safe_score
        }


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniNsfwFilterEngine:
    """
    Production Engine providing deep probabilistic moderation gating algebra.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-nsfw-filter"

    def __init__(self) -> None:
        self._gates_evaluated = 0

    def evaluate_probability_distribution(self, predictions_map: Dict[str, float], 
                                          explicit_block_level: float = 0.51, 
                                          soft_review_level: float = 0.70) -> Result:
        """Route computational boundaries mapping prediction floats to hard bool bounds."""
        if not predictions_map:
            return Err("Probabilistic mapping distributions cannot be empty.")
            
        # Ensure mapping is clean floats
        try:
            sanitized_map = {str(k).lower(): float(v) for k, v in predictions_map.items()}
        except ValueError:
            return Err("Prediction floats must be numerically evaluable boundaries.")
            
        if explicit_block_level < 0.0 or explicit_block_level > 1.0:
            return Err("Threshold boundaries must reside between probabilities 0.0 and 1.0.")

        try:
            assessment = ThresholdGatekeeper.evaluate_safety(
                prob_map=sanitized_map,
                explicit_thres=explicit_block_level,
                sensitive_thres=soft_review_level
            )
            
            self._gates_evaluated += 1
            
            return Ok({
                "moderation_resolution": assessment,
                "input_parameters": {
                    "explicit_threshold": explicit_block_level,
                    "review_threshold": soft_review_level
                }
            })
            
        except Exception as exc:
            return Err(f"Moderation vector routing failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "vectors_evaluated": self._gates_evaluated,
            "features": [
                "discrete_tensor_probability_gating",
                "nsfw_category_summation_matrix",
                "threshold_boolean_hardbounds"
            ]
        }
