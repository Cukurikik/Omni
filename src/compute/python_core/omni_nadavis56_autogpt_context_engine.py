from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniNadavis56AutogptContextEngine:
    """
    OMNI Framework Level-2 Abstraction Engine.
    Assimilated from: NadavIs56/AutoGPT-Telegram-bot

    Purpose: Validates conversational context window bounds for autonomous
    GPT-based chatbots. Enforces token budget constraints and conversation
    history truncation policies using sliding-window mathematics.
    Enforces OMNI ZERO-MOCK Policy and Monadic Error Handling.
    """

    @staticmethod
    def diagnostics() -> Dict[str, Any]:
        return {
            "engine": "OmniNadavis56AutogptContextEngine",
            "status": "operational",
            "layer": "Compute",
            "abstraction_level": "L2-ContextWindowBounds",
            "monadic_enforcement": True
        }

    @staticmethod
    def validate_context_window(message_token_counts: List[int], max_context_tokens: int, system_prompt_tokens: int) -> Result[int, Exception]:
        """
        Calculates how many recent messages fit within the token budget
        using a greedy sliding window from most recent to oldest.
        Returns the count of messages that fit.
        """
        if max_context_tokens <= 0:
            return Err(ValueError("max_context_tokens must be positive."))
        if system_prompt_tokens < 0:
            return Err(ValueError("system_prompt_tokens cannot be negative."))
        if system_prompt_tokens >= max_context_tokens:
            return Err(RuntimeError("System prompt alone exceeds context window. No room for conversation."))

        available_tokens = max_context_tokens - system_prompt_tokens
        consumed = 0
        messages_fit = 0

        # Iterate from most recent message backward
        for token_count in reversed(message_token_counts):
            if token_count < 0:
                return Err(ValueError("Token count for a message cannot be negative."))
            if consumed + token_count > available_tokens:
                break
            consumed += token_count
            messages_fit += 1

        return Ok(messages_fit)
