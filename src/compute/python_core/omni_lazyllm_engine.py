"""
OMNI LazyLLM Engine — Multi-agent LLM application builder primitives.

Assimilated from: LazyAGI/LazyLLM (3.1k ★)
Easiest and laziest way for building multi-agent LLMs applications.

Implements LLM orchestration building blocks:
  - Prompt template management with variable injection
  - Chain-of-thought decomposition
  - Tool/function calling schema definition
  - Multi-agent pipeline (sequential, parallel, routing)
  - Retrieval-augmented generation (RAG) pipeline primitives
  - Token counting and context window management
  - Conversation memory management (sliding window, summary)
  - Output parsing (JSON, list, key-value)

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import re
import json
import math
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniLazyLLMEngine"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class Result:
    """Monadic Result type for error handling."""
    pass

class Ok(Result):
    """Monadic Ok result type."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value

class Err(Result):
    """Monadic Err result type."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


class OmniLazyLLMEngine:
    """Production-grade multi-agent LLM application builder engine.

    Implements LLM orchestration patterns:
      - Prompt templates with variable injection
      - Chain-of-thought decomposition
      - Tool/function calling schemas
      - Multi-agent pipelines (sequential, parallel, routing)
      - RAG retrieval pipeline
      - Context window management
      - Conversation memory (sliding, summary)
      - Output parsing (JSON, list, kv)

    @since 1.0.0
    @tags ["llm", "multi-agent", "rag", "prompt-engineering", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniLazyLLMEngine."""
        pass

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniLazyLLMEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "render_prompt", "chain_of_thought", "tool_schema",
                "sequential_pipeline", "parallel_pipeline", "route",
                "rag_retrieve", "count_tokens", "sliding_window_memory",
                "parse_json_output", "parse_list_output",
            ],
        })

    # -----------------------------------------------------------------
    # 1. PROMPT MANAGEMENT
    # -----------------------------------------------------------------

    def render_prompt(self, template: str, variables: Dict[str, str]) -> Result:
        """Render a prompt template with variable injection.

        Templates use {variable_name} placeholder syntax.

        @param template: Template string with {placeholders}.
        @param variables: Dict of variable_name → value.
        @returns Result with rendered string.
        """
        rendered = template
        for key, val in variables.items():
            rendered = rendered.replace("{" + key + "}", str(val))
        # Check for unresolved placeholders
        unresolved = re.findall(r"\{(\w+)\}", rendered)
        if unresolved:
            return Err(f"Unresolved variables: {unresolved}")
        return Ok(rendered)

    def build_chat_messages(
        self, system_prompt: str, user_message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Result:
        """Build chat message array in OpenAI format.

        @param system_prompt: System message.
        @param user_message: User's current message.
        @param history: Previous [(role, content)] messages.
        @returns Result with list of message dicts.
        """
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return Ok(messages)

    # -----------------------------------------------------------------
    # 2. CHAIN-OF-THOUGHT
    # -----------------------------------------------------------------

    def chain_of_thought(self, question: str, steps: List[str]) -> Result:
        """Construct a chain-of-thought prompt.

        @param question: The original question.
        @param steps: List of reasoning steps.
        @returns Result with formatted CoT string.
        """
        cot = f"Question: {question}\n\nLet's think step by step:\n"
        for i, step in enumerate(steps, 1):
            cot += f"Step {i}: {step}\n"
        cot += "\nTherefore, the answer is:"
        return Ok(cot)

    def decompose_task(self, task: str, n_subtasks: int) -> Result:
        """Decompose a complex task into numbered subtasks (template).

        @param task: High-level task description.
        @param n_subtasks: Number of subtasks to plan.
        @returns Result with decomposition prompt.
        """
        prompt = f"Task: {task}\n\nBreak this into {n_subtasks} subtasks:\n"
        for i in range(1, n_subtasks + 1):
            prompt += f"  Subtask {i}: [TO_BE_FILLED]\n"
        return Ok(prompt)

    # -----------------------------------------------------------------
    # 3. TOOL / FUNCTION CALLING
    # -----------------------------------------------------------------

    def tool_schema(self, name: str, description: str, parameters: Dict[str, Dict[str, str]]) -> Result:
        """Define a tool/function calling schema (OpenAI format).

        @param name: Function name.
        @param description: Function description.
        @param parameters: Dict of param_name → {type, description}.
        @returns Result with tool schema dict.
        """
        props = {}
        required = []
        for pname, pinfo in parameters.items():
            props[pname] = {
                "type": pinfo.get("type", "string"),
                "description": pinfo.get("description", ""),
            }
            if pinfo.get("required", True):
                required.append(pname)

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                },
            },
        }
        return Ok(schema)

    def parse_tool_call(self, response_text: str) -> Result:
        """Parse tool call from LLM response (JSON block extraction).

        @param response_text: Raw LLM response containing JSON.
        @returns Result with parsed dict.
        """
        # Try extracting JSON from ```json ... ``` blocks
        match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            try:
                return Ok(json.loads(match.group(1)))
            except json.JSONDecodeError as e:
                return Err(f"JSON parse error: {e}")

        # Try raw JSON
        try:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            return Ok(json.loads(response_text[start:end]))
        except (ValueError, json.JSONDecodeError) as e:
            return Err(f"No valid JSON found: {e}")

    # -----------------------------------------------------------------
    # 4. MULTI-AGENT PIPELINE
    # -----------------------------------------------------------------

    def sequential_pipeline(self, inputs: Any, steps: List[Callable[[Any], Any]]) -> Result:
        """Execute pipeline steps sequentially, passing output → input.

        @param inputs: Initial input.
        @param steps: List of callable functions.
        @returns Result with final output.
        """
        current = inputs
        for i, step in enumerate(steps):
            try:
                current = step(current)
            except Exception as e:
                return Err(f"Pipeline step {i} failed: {e}")
        return Ok(current)

    def parallel_pipeline(self, inputs: Any, branches: List[Callable[[Any], Any]]) -> Result:
        """Execute branches in parallel-like fashion (sequential sim).

        @param inputs: Input data (shared).
        @param branches: List of callable functions.
        @returns Result with list of outputs.
        """
        outputs = []
        for i, branch in enumerate(branches):
            try:
                outputs.append(branch(inputs))
            except Exception as e:
                return Err(f"Branch {i} failed: {e}")
        return Ok(outputs)

    def route(self, query: str, routes: Dict[str, List[str]]) -> Result:
        """Simple keyword-based routing to agents/functions.

        @param query: User query.
        @param routes: Dict of route_name → list of trigger keywords.
        @returns Result with matched route name.
        """
        query_lower = query.lower()
        best_route = None
        best_score = 0
        for route_name, keywords in routes.items():
            score = sum(1 for kw in keywords if kw.lower() in query_lower)
            if score > best_score:
                best_score = score
                best_route = route_name
        if best_route is None:
            return Err("No matching route.")
        return Ok(best_route)

    # -----------------------------------------------------------------
    # 5. RAG RETRIEVAL
    # -----------------------------------------------------------------

    def rag_retrieve(
        self, query_embedding: np.ndarray, doc_embeddings: np.ndarray,
        doc_texts: List[str], top_k: int = 5
    ) -> Result:
        """Retrieve top-k relevant documents via cosine similarity.

        @param query_embedding: (D,) query vector.
        @param doc_embeddings: (N, D) document vectors.
        @param doc_texts: List of document texts.
        @param top_k: Number of documents to retrieve.
        @returns Result with list of (text, score) tuples sorted by relevance.
        """
        q_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        d_norms = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1, keepdims=True) + 1e-10)
        similarities = d_norms @ q_norm
        top_idx = np.argsort(similarities)[::-1][:top_k]
        results = [(doc_texts[i], float(similarities[i])) for i in top_idx]
        return Ok(results)

    def build_rag_prompt(self, question: str, contexts: List[str]) -> Result:
        """Build RAG prompt with retrieved contexts.

        @param question: User question.
        @param contexts: Retrieved document texts.
        @returns Result with formatted prompt.
        """
        ctx_block = "\n\n".join(f"[Context {i+1}]: {c}" for i, c in enumerate(contexts))
        prompt = (
            f"Answer the question based on the provided contexts.\n\n"
            f"{ctx_block}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        return Ok(prompt)

    # -----------------------------------------------------------------
    # 6. CONTEXT WINDOW MANAGEMENT
    # -----------------------------------------------------------------

    def count_tokens_approx(self, text: str) -> Result:
        """Approximate token count (words × 1.3 heuristic).

        @param text: Input text.
        @returns Result with approximate token count.
        """
        words = len(text.split())
        return Ok(int(words * 1.3))

    def truncate_to_fit(self, messages: List[Dict[str, str]], max_tokens: int) -> Result:
        """Truncate conversation history to fit context window.

        Keeps system message + most recent messages.

        @param messages: List of message dicts with 'content'.
        @param max_tokens: Maximum allowed tokens.
        @returns Result with truncated messages.
        """
        if not messages:
            return Ok([])

        total = sum(int(len(m["content"].split()) * 1.3) for m in messages)
        if total <= max_tokens:
            return Ok(messages)

        # Keep system (first) + truncate from oldest
        result = [messages[0]] if messages[0].get("role") == "system" else []
        remaining = messages[1:] if result else messages[:]

        for msg in reversed(remaining):
            cost = int(len(msg["content"].split()) * 1.3)
            total_kept = sum(int(len(m["content"].split()) * 1.3) for m in result) + cost
            if total_kept <= max_tokens:
                result.insert(len(result), msg)

        return Ok(result)

    # -----------------------------------------------------------------
    # 7. CONVERSATION MEMORY
    # -----------------------------------------------------------------

    def sliding_window_memory(self, history: List[Dict[str, str]], window_size: int) -> Result:
        """Keep only the last N messages (sliding window).

        @param history: Full conversation history.
        @param window_size: Number of messages to keep.
        @returns Result with truncated history.
        """
        return Ok(history[-window_size:])

    # -----------------------------------------------------------------
    # 8. OUTPUT PARSING
    # -----------------------------------------------------------------

    def parse_json_output(self, text: str) -> Result:
        """Parse JSON from LLM output text.

        @param text: Raw text output.
        @returns Result with parsed dict/list.
        """
        return self.parse_tool_call(text)

    def parse_list_output(self, text: str) -> Result:
        """Parse numbered or bulleted list from LLM output.

        @param text: Raw text with list items.
        @returns Result with list of strings.
        """
        lines = text.strip().split("\n")
        items = []
        for line in lines:
            cleaned = re.sub(r"^[\d\.\-\*\)\s]+", "", line).strip()
            if cleaned:
                items.append(cleaned)
        return Ok(items)
