"""OmniChatDevWaterfallEngine.

Implements phase transition constraints for the ChatDev 
software engineering waterfall framework.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniChatDevWaterfallEngine:
    """Zero-mock engine for ChatDev waterfall phase transitions."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniChatDevWaterfallEngine",
            "version": "1.0.0",
            "primitive": "waterfall_phase_transition",
            "monadic_enforcement": True,
        }

    @staticmethod
    def validate_phase_transition(current_phase: str, artifacts_present: List[str]) -> Result:
        """
        Ensures strict dependencies are met before moving to the next
        phase in the ChatDev waterfall.
        """
        if not current_phase:
            return Err(ValueError("Current phase is required"))
            
        phase = current_phase.upper()
        missing_artifacts = []
        is_ready = True
        
        if phase == "CODING":
            if "design_doc.txt" not in artifacts_present:
                is_ready = False
                missing_artifacts.append("design_doc.txt")
        elif phase == "TESTING":
            if "main.py" not in artifacts_present: # simplified check
                is_ready = False
                missing_artifacts.append("source_code")
        elif phase == "DOCUMENTING":
            if "test_results.log" not in artifacts_present:
                is_ready = False
                missing_artifacts.append("test_results.log")
                
        return Ok({
            "phase_evaluated": phase,
            "is_ready_for_transition": is_ready,
            "missing_artifacts": missing_artifacts
        })
