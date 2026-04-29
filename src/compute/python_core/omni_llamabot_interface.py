# Omni LlamaBot Pythonic LLM Interface
# Ref: ericmjl/llamabot — MIT
from typing import List, Dict, Optional

def build_system_prompt(preamble: str, examples: List[Dict] = None) -> str:
    prompt = preamble
    if examples:
        for ex in examples[:5]:
            prompt += f"\nUser: {ex.get('input','')}\nAssistant: {ex.get('output','')}"
    return prompt

def chat_turn(history: List[Dict], user_msg: str, system: str = "") -> List[Dict]:
    if system and not history:
        history.append({"role": "system", "content": system})
    history.append({"role": "user", "content": user_msg})
    return history

def token_count_estimate(messages: List[Dict]) -> int:
    return sum(len(m.get("content","").split()) for m in messages)

def truncate_to_budget(messages: List[Dict], max_tokens: int = 4096) -> List[Dict]:
    total = 0; result = []
    for m in reversed(messages):
        n = len(m.get("content","").split())
        if total + n > max_tokens: break
        result.insert(0, m); total += n
    return result
