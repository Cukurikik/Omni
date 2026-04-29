# Omni LibreChat API Engine
# Ref: vemonet/libre-chat
from typing import List, Dict

def format_librechat_payload(messages: List[Dict[str, str]], model: str = "omni-base-1") -> Dict:
    """Format standard chat history into LibreChat compatible API payload."""
    valid_roles = {"user", "assistant", "system"}
    formatted_msgs = []
    
    for msg in messages:
        role = msg.get("role", "user")
        if role not in valid_roles:
            role = "user"
        formatted_msgs.append({"role": role, "content": msg.get("content", "")})
        
    return {
        "model": model,
        "messages": formatted_msgs,
        "temperature": 0.7,
        "stream": False
    }

def calculate_chat_session_cost(messages: List[Dict[str, str]], cost_per_1k: float = 0.002) -> float:
    """Estimate cost of a LibreChat session based on word count."""
    total_words = sum(len(msg.get("content", "").split()) for msg in messages)
    estimated_tokens = total_words * 1.3  # Rough token multiplier
    return round((estimated_tokens / 1000.0) * cost_per_1k, 6)

def parse_librechat_response(raw_response: Dict) -> str:
    """Extract content from LibreChat response structure."""
    try:
        return raw_response.get("choices", [{}])[0].get("message", {}).get("content", "")
    except (IndexError, AttributeError):
        return ""
