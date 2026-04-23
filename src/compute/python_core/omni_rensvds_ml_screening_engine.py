from typing import Dict, Any
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniRensvdsMlScreeningEngine:
    """
    OMNI Framework Level-2 Abstraction Engine.
    Assimilated from: Rensvandeschoot/software-overview-machine-learning-for-screening-text

    Purpose: Active Learning screening threshold calculator. Determines
    the mathematically optimal stopping point for document screening
    using recall-based saturation curves (Work Saved over Sampling - WSS).
    Enforces OMNI ZERO-MOCK Policy and Monadic Error Handling.
    """

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniRensvdsMlScreeningEngine",
            "status": "operational",
            "layer": "Compute",
            "abstraction_level": "L2-ActiveLearningThreshold",
            "monadic_enforcement": True
        }

    @staticmethod
    def calculate_wss_at_recall(total_documents: int, relevant_found: int, total_relevant: int, documents_screened: int, target_recall: float = 0.95) -> Result[float, Exception]:
        """
        Work Saved over Sampling at a given recall level.
        WSS@recall = (TN + FN) / N - (1 - recall)
        Simplified: WSS = 1 - (documents_screened / total_documents) - (1 - current_recall)
        """
        if total_documents <= 0:
            return Err(ValueError("total_documents must be positive."))
        if total_relevant <= 0:
            return Err(ValueError("total_relevant must be positive."))
        if documents_screened < 0 or documents_screened > total_documents:
            return Err(ValueError("documents_screened must be between 0 and total_documents."))
        if relevant_found < 0 or relevant_found > total_relevant:
            return Err(ValueError("relevant_found cannot exceed total_relevant."))
        if not (0.0 < target_recall <= 1.0):
            return Err(ValueError("target_recall must be in (0, 1]."))

        current_recall = relevant_found / total_relevant
        screening_fraction = documents_screened / total_documents
        wss = (1.0 - screening_fraction) - (1.0 - current_recall)

        if current_recall < target_recall:
            return Err(RuntimeError(
                f"Target recall {target_recall} not yet met. Current recall: {current_recall:.4f}. "
                f"Continue screening."
            ))

        return Ok(round(wss, 6))
