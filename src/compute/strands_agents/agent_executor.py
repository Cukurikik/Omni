from typing import List, Dict, Callable

class AgentExecutor:
    """
    OMNI Engine: strands-agents Model-Driven execution loop.
    """
    def __init__(self, llm_client, tools: List[Callable]):
        self.llm = llm_client
        self.tools = {t.__name__: t for t in tools}
        self.memory = []

    def run(self, task: str) -> str:
        self.memory.append({"role": "user", "content": task})
        
        for _ in range(10): # max steps
            response = self.llm.generate(self.memory)
            self.memory.append({"role": "assistant", "content": response.content})
            
            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_func = self.tools.get(tc.name)
                    if tool_func:
                        result = tool_func(**tc.args)
                        self.memory.append({"role": "tool", "name": tc.name, "content": str(result)})
            else:
                return response.content
                
        return "Agent stopped: Max steps reached."
