# Omni LLM API Key Manager Engine
# Ref: alistaitsacle/free-llm-api-keys — MIT
import hashlib, time
from typing import List, Dict

def validate_api_key(key: str, provider: str = "openai") -> Dict:
    if not key or len(key) < 10: return {"valid": False, "reason": "too_short"}
    prefixes = {"openai": "sk-", "anthropic": "sk-ant-", "google": "AIza"}
    expected = prefixes.get(provider, "")
    if expected and not key.startswith(expected): return {"valid": False, "reason": "wrong_prefix"}
    return {"valid": True, "provider": provider, "masked": key[:8] + "..." + key[-4:]}

def rotate_keys(keys: List[str], current_idx: int = 0) -> Dict:
    if not keys: return {"key": None, "idx": -1}
    idx = (current_idx + 1) % len(keys)
    return {"key": keys[idx][:8] + "...", "idx": idx, "total_keys": len(keys)}

def key_usage_stats(usage_log: List[Dict]) -> Dict:
    total_tokens = sum(u.get("tokens", 0) for u in usage_log)
    total_cost = sum(u.get("cost", 0) for u in usage_log)
    return {"total_requests": len(usage_log), "total_tokens": total_tokens, "total_cost": round(total_cost, 4)}
