# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# LangChain Agent Executor (OMNI Zero-Mock Implementation)
# Implements action parsing and sequence execution.

from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class Result:
    value: Optional[Any]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Any) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AgentExecutor:
    def __init__(self, tools: Dict[str, callable]):
        self.tools = tools

    def execute_action(self, action_type: str, action_input: str) -> Result:
        if not action_type:
             return Result.err("Action type is required.")
             
        if action_type not in self.tools:
             return Result.err(f"Tool {action_type} is not registered in this agent.")
             
        try:
             output = self.tools[action_type](action_input)
             return Result.ok(output)
        except Exception as e:
             return Result.err(f"Execution failed: {str(e)}")

    def run_sequence(self, actions: List[Dict[str, str]]) -> Result:
        results = []
        for action in actions:
            if "type" not in action or "input" not in action:
                return Result.err("Malformed action payload.")
                
            res = self.execute_action(action["type"], action["input"])
            if not res.is_ok:
                 return res
            results.append(res.value)
            
        return Result.ok(results)
