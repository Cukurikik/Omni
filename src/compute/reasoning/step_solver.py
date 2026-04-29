from typing import List, Dict, Optional, Tuple
import json

# OMNI REASONING: Step-by-Step Solver
# Pure Python reasoning logic for LLM scratchpads, avoiding frameworks.
# Source: rasbt/reasoning-from-scratch

class StepError(Exception):
    pass

class ReasoningSolver:
    """
    Implements Chain-of-Thought (CoT) tracking for deterministic reasoning.
    Enforces monadic-like Result returns for stability.
    """
    
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.current_step = 0
        self.history: List[Dict[str, str]] = []

    def solve(self, prompt: str, llm_callable) -> Tuple[Optional[str], Optional[StepError]]:
        """
        Iteratively queries the LLM callable until a final answer is reached
        or max steps are exhausted.
        """
        self.history.append({"role": "user", "content": prompt})
        
        while self.current_step < self.max_steps:
            try:
                # LLM callable must return (thought, action, is_final)
                thought, action, is_final = llm_callable(self.history)
                
                self.history.append({
                    "role": "assistant", 
                    "content": f"Thought: {thought}\nAction: {action}"
                })
                
                if is_final:
                    return action, None
                    
                # Execute action locally (e.g. math evaluation, API call)
                observation = self._execute_action(action)
                self.history.append({"role": "system", "content": f"Observation: {observation}"})
                
                self.current_step += 1
                
            except Exception as e:
                return None, StepError(f"Reasoning failure at step {self.current_step}: {str(e)}")
                
        return None, StepError("Max reasoning steps exhausted.")

    def _execute_action(self, action: str) -> str:
        """
        Strictly sandboxed execution of a reasoning action.
        """
        # Parse action string -> { "tool": "calc", "args": "5 * 5" }
        try:
            payload = json.loads(action)
            tool = payload.get("tool")
            args = payload.get("args")
            
            if tool == "calculator":
                # Only allow pure math expressions (No eval!)
                allowed_chars = "0123456789+-*/(). "
                if not all(c in allowed_chars for c in args):
                    return "Error: Invalid characters in math expression."
                # Safe eval proxy
                return str(eval(args, {"__builtins__": None}, {}))
                
            elif tool == "search":
                return f"Simulated search results for: {args}"
            else:
                return f"Error: Tool '{tool}' not found."
                
        except json.JSONDecodeError:
            return "Error: Action must be valid JSON."
        except Exception as e:
            return f"Error executing action: {str(e)}"

# Example LLM Callable stub
def dummy_llm(history):
    if len(history) < 3:
        return ("I need to calculate 15 * 7", '{"tool": "calculator", "args": "15 * 7"}', False)
    else:
        return ("I have the answer.", "The answer is 105.", True)
