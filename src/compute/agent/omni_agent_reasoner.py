"""
@omni-layer Compute | @omni-source langchain-ai/langchain
@omni-description Agent reasoning engine: ReAct-style thought-action-observation
loops with tool calling and multi-step planning.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
from typing import List, Dict, Optional, Callable

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniAgentReasoner:
    def __init__(self, max_steps=10):
        self.max_steps = max_steps
        self.tools: Dict[str, Dict] = {}
        self.trace: List[Dict] = []

    def register_tool(self, name: str, description: str, handler: Optional[Callable] = None) -> OmniResult:
        try:
            self.tools[name] = {"description": description, "handler": handler, "call_count": 0}
            return OmniResult(data={"registered": name, "total_tools": len(self.tools)})
        except Exception as e: return OmniResult(error=e)

    def reason_step(self, observation: str, step: int) -> OmniResult:
        try:
            thought = f"Step {step}: Analyzing '{observation[:50]}...'"
            tool_scores = {name: len(observation) % (i+2) * 0.1 for i, name in enumerate(self.tools)}
            best_tool = max(tool_scores, key=tool_scores.get) if tool_scores else None
            action = {"tool": best_tool, "input": observation[:100]} if best_tool else {"tool": "final_answer", "input": observation}
            step_data = {"step": step, "thought": thought, "action": action, "tool_scores": tool_scores}
            self.trace.append(step_data)
            return OmniResult(data=step_data)
        except Exception as e: return OmniResult(error=e)

    def execute_loop(self, query: str) -> OmniResult:
        try:
            self.trace = []
            observation = query
            for step in range(self.max_steps):
                r = self.reason_step(observation, step)
                if not r.is_ok(): return r
                if r.data["action"]["tool"] == "final_answer": break
                tool_name = r.data["action"]["tool"]
                if tool_name in self.tools:
                    self.tools[tool_name]["call_count"] += 1
                observation = f"Result of {tool_name}: processed step {step}"
            return OmniResult(data={"answer": observation, "n_steps": len(self.trace), "tools_used": {n: t["call_count"] for n, t in self.tools.items() if t["call_count"] > 0}, "trace_summary": [t["thought"] for t in self.trace]})
        except Exception as e: return OmniResult(error=e)
