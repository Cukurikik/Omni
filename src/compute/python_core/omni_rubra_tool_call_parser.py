# Omni Rubra Tool Call Parser (Python)
# Compute Layer: Deterministic function-calling parser for open-weight LLMs.
# Ref: rubra-ai/rubra — Open weight tool-calling LLMs.

import json
from typing import List, Dict, Optional

class ToolCall:
    __slots__ = ('name', 'arguments', 'call_id')
    def __init__(self, name: str, arguments: Dict, call_id: str):
        self.name = name
        self.arguments = arguments
        self.call_id = call_id

def parse_tool_calls(raw_output: str) -> List[ToolCall]:
    calls: List[ToolCall] = []
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        return calls
    if isinstance(data, list):
        for i, item in enumerate(data):
            if 'name' in item and 'arguments' in item:
                calls.append(ToolCall(item['name'], item['arguments'], f"call_{i}"))
    elif isinstance(data, dict) and 'name' in data:
        calls.append(ToolCall(data['name'], data.get('arguments', {}), 'call_0'))
    return calls

def validate_tool_schema(call: ToolCall, schema: Dict[str, type]) -> bool:
    for param, expected_type in schema.items():
        if param not in call.arguments:
            return False
        if not isinstance(call.arguments[param], expected_type):
            return False
    return True
