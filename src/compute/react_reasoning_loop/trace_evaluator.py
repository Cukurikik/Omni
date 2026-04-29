class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TraceEvaluator:
    def __init__(self):
        pass

    def evaluate_react_trace(self, thought: str, action: str, observation: str) -> OmniResult:
        if not thought or not action:
            return OmniResult(error="Thought and Action are required for ReAct loops")

        # Deterministic simulation of ReAct (Reasoning and Acting) loop evaluation
        # Used to parse and evaluate the internal monologue of an Agentic RAG system
        try:
            is_valid = True
            reason = "Trace is logically sound"

            if "cannot determine" in observation.lower() and "search" not in action.lower():
                is_valid = False
                reason = "Agent failed to search when observation was inconclusive"

            if len(thought) < 10:
                is_valid = False
                reason = "Thought process is too shallow, prompt injection likely"

            return OmniResult(value={"valid": is_valid, "reason": reason})
        except Exception as e:
            return OmniResult(error=str(e))
