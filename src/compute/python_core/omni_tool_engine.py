"""OMNI Compute — Function Calling / Tool Use Engine"""
import json, logging, time, re; from dataclasses import dataclass, field; from typing import Dict, List, Any, Callable, Optional
logger = logging.getLogger("omni.tools")

@dataclass
class ToolDefinition:
    name: str; description: str; parameters: Dict; handler: Optional[Callable] = None

class OmniToolEngine:
    """Parse and execute function calls from LLM output."""
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.call_log: List[Dict] = []
    def register(self, tool: ToolDefinition):
        self.tools[tool.name] = tool
    def get_tools_prompt(self) -> str:
        defs = []
        for t in self.tools.values():
            defs.append({"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}})
        return json.dumps(defs, indent=2)
    def parse_tool_calls(self, output: str) -> List[Dict]:
        calls = []
        # Pattern 1: OpenAI-style
        pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        for match in re.finditer(pattern, output, re.DOTALL):
            try: calls.append(json.loads(match.group(1)))
            except: pass
        # Pattern 2: JSON array
        if not calls:
            try:
                parsed = json.loads(output)
                if isinstance(parsed, list): calls = parsed
                elif isinstance(parsed, dict) and "name" in parsed: calls = [parsed]
            except: pass
        return calls
    def execute(self, call: Dict) -> Dict:
        name = call.get("name", "")
        args = call.get("arguments", call.get("args", {}))
        if isinstance(args, str):
            try: args = json.loads(args)
            except: args = {}
        tool = self.tools.get(name)
        if not tool: return {"error": f"Unknown tool: {name}"}
        start = time.time()
        try:
            if tool.handler: result = tool.handler(**args)
            else: result = {"status": "no_handler", "tool": name, "args": args}
            elapsed = (time.time() - start) * 1000
            log_entry = {"tool": name, "args": args, "result": result, "latency_ms": elapsed}
            self.call_log.append(log_entry)
            return result
        except Exception as e:
            return {"error": str(e), "tool": name}
    def execute_all(self, output: str) -> List[Dict]:
        calls = self.parse_tool_calls(output)
        return [self.execute(c) for c in calls]
    def stats(self) -> Dict:
        return {"total_calls": len(self.call_log), "tools_registered": len(self.tools),
                "tools": list(self.tools.keys())}
