"""OmniStatefulConversationThreadEngine — Sliding Window LLM Context.

Inspired by vedant007-v/codex_dspy: a tool to simplify multi-turn
conversations for OpenAI Codex, offering stateful threads and rich,
typed context management.

Algorithmic Primitive:
    Maintain conversation memory locally. Expose methods to append
    user/assistant turns and gracefully implement sliding-window 
    context truncation to prevent token overflow while preserving
    important system instructions.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniStatefulConversationThreadEngine:
    """Production-grade LLM stateful conversation thread manager."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniStatefulConversationThreadEngine",
            "version": "1.0.0",
            "primitive": "stateful_thread_sliding_window_truncation",
            "monadic_enforcement": True,
            "source_repo": "vedant007-v/codex_dspy",
        }

    @staticmethod
    def add_message(
        thread: list[dict],
        role: str,
        content: str,
    ) -> Result:
        """Append a generic conversational message to a thread log.

        Args:
            thread: Existing list of message dictionaries.
            role: e.g., 'system', 'user', 'assistant'.
            content: The message payload.

        Returns:
            Result[list[dict], Exception]: A new cloned thread with the message added.
        """
        if not isinstance(thread, list):
            return Err(Exception("thread must be a list"))
        if role not in ("system", "user", "assistant", "tool"):
            return Err(Exception(f"Unsupported role: '{role}'"))
        if not isinstance(content, str):
            return Err(Exception("content must be a string"))

        new_thread = [m.copy() for m in thread]
        new_thread.append({"role": role, "content": content})
        return Ok(new_thread)

    @staticmethod
    def truncate_sliding_window(
        thread: list[dict],
        max_messages: int = 10,
        preserve_system: bool = True,
    ) -> Result:
        """Truncate the conversation history using a sliding window.

        Args:
            thread: The full continuous conversation record.
            max_messages: The max number of messages to keep.
            preserve_system: Never truncate the first 'system' instruction.

        Returns:
            Result[list[dict], Exception]: The truncated conversation sequence.
        """
        if not isinstance(thread, list):
            return Err(Exception("thread must be a list"))
        if max_messages < 1:
            return Err(Exception("max_messages must be at least 1"))

        if len(thread) <= max_messages:
            return Ok([m.copy() for m in thread])

        system_messages = []
        regular_messages = []

        for msg in thread:
            if preserve_system and msg.get("role") == "system":
                system_messages.append(msg.copy())
            else:
                regular_messages.append(msg.copy())

        # The effective budget for recent regular messages
        budget = max_messages - len(system_messages)
        if budget < 0:
            budget = 0

        truncated = system_messages + regular_messages[-budget:] if budget > 0 else system_messages
        return Ok(truncated)
