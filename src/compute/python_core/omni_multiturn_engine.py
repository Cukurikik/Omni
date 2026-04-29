# Omni Multi-Turn Conversation Engine
# Ref: yubol-bobo/Awesome-Multi-Turn-LLMs — MIT
from typing import List, Dict
def build_conversation(turns: List[Dict]) -> List[Dict]:
    return [{"role": t.get("role","user"), "content": t.get("content",""), "turn": i+1} for i,t in enumerate(turns)]
def context_window_usage(turns: List[Dict], max_tokens: int = 4096) -> Dict:
    total = sum(len(t.get("content","").split()) for t in turns)
    return {"total_tokens": total, "max_tokens": max_tokens, "usage_pct": round(total/max_tokens*100,1),
            "overflow": total > max_tokens}
def turn_consistency(responses: List[str]) -> float:
    if len(responses) < 2: return 1.0
    pairs = [(responses[i], responses[i+1]) for i in range(len(responses)-1)]
    consistency = sum(1 for a,b in pairs if len(set(a.split())&set(b.split()))>2) / len(pairs)
    return round(consistency, 4)
def truncate_history(turns: List[Dict], max_tokens: int) -> List[Dict]:
    total = 0; result = []
    for t in reversed(turns):
        n = len(t.get("content","").split())
        if total + n > max_tokens: break
        result.insert(0, t); total += n
    return result
