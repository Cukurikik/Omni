"""OmniKotaemonRAGEngine.

Provides UI-centric retrieval structural limits for the
Kotaemon open-source RAG UI architecture.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniKotaemonRAGEngine:
    """Zero-mock engine for Kotaemon UI-centric RAG logic."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniKotaemonRAGEngine",
            "version": "1.0.0",
            "primitive": "ui_rag_chunk_limiter",
            "monadic_enforcement": True,
        }

    @staticmethod
    def limit_display_chunks(chunks: List[Dict[str, Any]], max_chars: int = 1500) -> Result:
        """
        Kotaemon emphasizes clean UI. This bounds the total characters
        to prevent UI overflow while maintaining highest confidence chunks.
        """
        if not chunks:
            return Err(ValueError("No chunks provided"))
            
        # Sort by confidence/score if available
        sorted_chunks = sorted(chunks, key=lambda x: x.get("score", 0.0), reverse=True)
        
        display_chunks = []
        current_chars = 0
        
        for chunk in sorted_chunks:
            text = chunk.get("text", "")
            if current_chars + len(text) <= max_chars:
                display_chunks.append(chunk)
                current_chars += len(text)
            else:
                break
                
        return Ok({
            "display_chunks": display_chunks,
            "total_chars_used": current_chars,
            "chunks_omitted": len(chunks) - len(display_chunks)
        })
