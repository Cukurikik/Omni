# Omni OgbujiPT LLM Client Toolkit
# Ref: OoriData/OgbujiPT — Apache-2.0
from typing import Dict, List

def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
    words = text.split(); chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + max_tokens]))
        i += max_tokens - overlap
    return chunks

def token_estimate(text: str) -> int:
    return max(1, int(len(text) / 4))

def trim_to_context(text: str, max_ctx: int = 4096) -> str:
    est = token_estimate(text)
    if est <= max_ctx: return text
    ratio = max_ctx / est
    return text[:int(len(text) * ratio)]
