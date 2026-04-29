"""OmniSelfRAGReflectionEngine.

Processes special critique tokens ([Retrieve], [Relevant], [Fully Supported])
for self-reflective RAG architectures.
"""
import sys
import os
import re
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniSelfRAGReflectionEngine:
    """Zero-mock engine for Self-RAG critique token parsing."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniSelfRAGReflectionEngine",
            "version": "1.0.0",
            "primitive": "critique_token_evaluator",
            "monadic_enforcement": True,
        }

    @staticmethod
    def evaluate_critique_tokens(output_text: str) -> Result:
        """
        Self-RAG models emit reflection tokens during generation.
        This parses them to determine the confidence and factuality of the output.
        """
        if not output_text:
            return Err(ValueError("Empty output text"))
            
        tokens_found = re.findall(r"\[(.*?)\]", output_text)
        
        critique_metrics = {
            "retrieval_called": False,
            "is_relevant": 0.0,
            "is_supported": 0.0,
            "is_useful": 0.0
        }
        
        relevant_count = 0
        supported_count = 0
        useful_count = 0
        
        for t in tokens_found:
            t_lower = t.lower()
            if "retrieve" in t_lower:
                critique_metrics["retrieval_called"] = True
            if "relevant" in t_lower and "irrelevant" not in t_lower:
                relevant_count += 1
            if "fully supported" in t_lower or "partially supported" in t_lower:
                supported_count += 1
            if "useful" in t_lower and "not useful" not in t_lower:
                useful_count += 1
                
        total_reflections = max(1, len([t for t in tokens_found if t_lower != "retrieve"]))
        
        critique_metrics["is_relevant"] = min(1.0, relevant_count / total_reflections)
        critique_metrics["is_supported"] = min(1.0, supported_count / total_reflections)
        critique_metrics["is_useful"] = min(1.0, useful_count / total_reflections)
        
        return Ok({
            "metrics": critique_metrics,
            "tokens_found": tokens_found,
            "requires_correction": critique_metrics["is_supported"] < 0.5
        })
