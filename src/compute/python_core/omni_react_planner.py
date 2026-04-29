from typing import Dict, Any

class OmniReActPlanner:
    """OMNI Compute Layer: ReAct (Reasoning and Acting) Engine"""
    
    def __init__(self):
        self.step_count = 0

    def parse_react_turn(self, llm_output: str) -> Dict[str, str]:
        self.step_count += 1
        
        lines = llm_output.strip().split('\\n')
        thought = ""
        action = ""
        
        for line in lines:
            if line.startswith("Thought:"):
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                action = line[7:].strip()
                
        return {
            "thought": thought,
            "action": action,
            "step": str(self.step_count)
        }
