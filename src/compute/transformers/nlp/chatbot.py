"""
OMNI Transformer — Chatbot with Dialogue History
Multi-turn conversation transformer with context management.
Learned from: pszemraj/ai-msgbot
"""
import torch
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ChatConfig:
    max_context_turns: int = 20
    max_context_tokens: int = 4096
    system_prompt: str = "You are a helpful AI assistant."
    temperature: float = 0.7
    top_p: float = 0.9
    max_new_tokens: int = 512


class DialogueManager:
    """Manage multi-turn conversation context."""
    def __init__(self, config: ChatConfig):
        self.config = config
        self.history: List[ChatMessage] = []
        if config.system_prompt:
            self.history.append(ChatMessage(role="system", content=config.system_prompt))

    def add_message(self, role: str, content: str) -> None:
        self.history.append(ChatMessage(role=role, content=content))
        self._trim_history()

    def _trim_history(self) -> None:
        # Keep system prompt + last N turns
        system_msgs = [m for m in self.history if m.role == "system"]
        other_msgs = [m for m in self.history if m.role != "system"]
        max_others = self.config.max_context_turns * 2
        if len(other_msgs) > max_others:
            other_msgs = other_msgs[-max_others:]
        self.history = system_msgs + other_msgs

    def format_prompt(self, tokenizer=None) -> str:
        parts = []
        for msg in self.history:
            if msg.role == "system":
                parts.append(f"<|system|>{msg.content}")
            elif msg.role == "user":
                parts.append(f"<|user|>{msg.content}")
            elif msg.role == "assistant":
                parts.append(f"<|assistant|>{msg.content}")
        parts.append("<|assistant|>")
        prompt = "\n".join(parts)

        if tokenizer:
            encoded = tokenizer.encode(prompt, max_length=self.config.max_context_tokens, truncation=True)
            prompt = tokenizer.decode(encoded["input_ids"])
        return prompt

    def clear(self) -> None:
        system = [m for m in self.history if m.role == "system"]
        self.history = system


class OmniChatbot:
    """Production chatbot with multi-turn dialogue management."""
    def __init__(self, model, tokenizer, config: ChatConfig = None):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or ChatConfig()
        self.sessions: Dict[str, DialogueManager] = {}

    def get_session(self, session_id: str) -> DialogueManager:
        if session_id not in self.sessions:
            self.sessions[session_id] = DialogueManager(self.config)
        return self.sessions[session_id]

    @torch.inference_mode()
    def chat(self, session_id: str, user_message: str) -> str:
        session = self.get_session(session_id)
        session.add_message("user", user_message)
        prompt = session.format_prompt(self.tokenizer)

        encoded = self.tokenizer.encode(prompt, max_length=self.config.max_context_tokens)
        input_ids = torch.tensor([encoded["input_ids"]], device=next(self.model.parameters()).device)

        if hasattr(self.model, "generate"):
            output_ids = self.model.generate(
                input_ids, max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature, top_p=self.config.top_p,
            )
            new_tokens = output_ids[0, input_ids.size(1):].tolist()
        else:
            output = self.model(input_ids)
            logits = output["logits"] if isinstance(output, dict) else output
            new_tokens = logits[0, -1].argmax().unsqueeze(0).tolist()

        response = self.tokenizer.decode(new_tokens)
        # Clean up special tokens
        for stop in ["<|user|>", "<|system|>", "<|end|>"]:
            if stop in response:
                response = response[:response.index(stop)]

        session.add_message("assistant", response.strip())
        return response.strip()

    def reset_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.sessions[session_id].clear()
