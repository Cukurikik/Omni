# Omni Conversant Persona Engine
# Ref: cohere-ai/sandbox-conversant-lib — MIT
from typing import List, Dict

def create_persona(name: str, preamble: str, examples: List[Dict] = None) -> Dict:
    return {"name": name, "preamble": preamble, "examples": examples or [], "turn_count": 0}

def build_chat_context(persona: Dict, history: List[Dict], max_turns: int = 10) -> str:
    ctx = f"Persona: {persona['preamble']}\n\n"
    for turn in history[-max_turns:]:
        ctx += f"{turn['role'].capitalize()}: {turn['content']}\n"
    return ctx

def conversation_quality(turns: List[Dict]) -> Dict:
    if not turns: return {"coherence": 0, "avg_length": 0}
    lengths = [len(t.get("content","").split()) for t in turns]
    return {"avg_length": round(sum(lengths)/len(lengths),1), "n_turns": len(turns), "coherence": round(min(1.0, len(turns)/10), 2)}
