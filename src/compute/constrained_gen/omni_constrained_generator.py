"""
@omni-layer Compute | @omni-source guidance-ai/guidance
@omni-description Constrained generation engine: grammar-guided decoding with
regex/CFG constraints for structured LLM output.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math, re
from typing import List, Optional, Set

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniConstrainedGenerator:
    def __init__(self, vocab_size=30000):
        self.vocab_size = vocab_size
        self.vocab_tokens = [f"tok_{i}" for i in range(min(vocab_size, 1000))]

    def regex_mask(self, pattern: str, partial_text: str) -> OmniResult:
        try:
            allowed_ids: List[int] = []
            for i, tok in enumerate(self.vocab_tokens[:100]):
                candidate = partial_text + tok
                try:
                    if re.match(pattern, candidate) or re.match(pattern[:len(candidate)], candidate):
                        allowed_ids.append(i)
                except re.error: pass
            if not allowed_ids: allowed_ids = list(range(min(10, len(self.vocab_tokens))))
            return OmniResult(data={"allowed_tokens": len(allowed_ids), "mask_ratio": len(allowed_ids)/max(len(self.vocab_tokens[:100]),1), "pattern": pattern})
        except Exception as e: return OmniResult(error=e)

    def json_constrained_decode(self, logits: List[float], context: str, expected_keys: List[str]) -> OmniResult:
        try:
            if context.endswith("{") or context.endswith(","):
                allowed = [f'"{k}"' for k in expected_keys]
                return OmniResult(data={"next_options": allowed, "context_type": "key"})
            elif context.endswith(":"):
                return OmniResult(data={"next_options": ["string", "number", "bool"], "context_type": "value"})
            return OmniResult(data={"next_options": ["any"], "context_type": "free"})
        except Exception as e: return OmniResult(error=e)

    def apply_bias(self, logits: List[float], allowed_ids: Set[int], bias: float = 100.0) -> OmniResult:
        try:
            biased = [l + bias if i in allowed_ids else l - bias for i, l in enumerate(logits)]
            return OmniResult(data={"biased_logits_sample": biased[:10], "n_allowed": len(allowed_ids)})
        except Exception as e: return OmniResult(error=e)
