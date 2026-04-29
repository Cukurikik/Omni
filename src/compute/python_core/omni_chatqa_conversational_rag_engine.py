"""OmniChatQAConversationalRAGEngine.

Optimized contextual retrieval integration and conversational history
chunking for ChatQA-style multi-turn RAG architectures.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniChatQAConversationalRAGEngine:
    """Zero-mock engine for conversational RAG context management."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniChatQAConversationalRAGEngine",
            "version": "1.0.0",
            "primitive": "conversational_context_manager",
            "monadic_enforcement": True,
        }

    @staticmethod
    def format_multi_turn_context(history: List[Dict[str, str]], retrieved_chunks: List[str], max_tokens: int = 4096) -> Result:
        """
        Formats conversational history alongside retrieved RAG chunks,
        prioritizing recent turns and highly relevant chunks.
        """
        if not history and not retrieved_chunks:
            return Err(ValueError("Both history and retrieved chunks are empty"))
            
        # Simplified token length estimation
        def estimate_tokens(text: str) -> int:
            return len(text.split()) * 1.3
            
        formatted_prompt = ""
        current_tokens = 0
        
        # 1. Add System/RAG Context first (usually highest priority in ChatQA)
        context_str = "Context information is below.\n---------------------\n"
        for chunk in retrieved_chunks:
            chunk_tokens = estimate_tokens(chunk)
            if current_tokens + chunk_tokens < (max_tokens * 0.6): # reserve 40% for history
                context_str += f"{chunk}\n---------------------\n"
                current_tokens += chunk_tokens
            else:
                break
                
        formatted_prompt += context_str
        
        # 2. Add conversational history (reversed to prioritize recent, then reverse back)
        history_str = "Conversation History:\n"
        history_lines = []
        
        for turn in reversed(history):
            role = turn.get("role", "user")
            content = turn.get("content", "")
            line = f"{role.capitalize()}: {content}\n"
            line_tokens = estimate_tokens(line)
            
            if current_tokens + line_tokens < max_tokens:
                history_lines.append(line)
                current_tokens += line_tokens
            else:
                break
                
        history_str += "".join(reversed(history_lines))
        formatted_prompt += history_str
        
        return Ok({
            "formatted_prompt": formatted_prompt.strip(),
            "estimated_tokens": int(current_tokens),
            "chunks_used": len(retrieved_chunks),
            "history_turns_used": len(history_lines)
        })
