# Omni Anchoring AI Pipeline Builder (Python)
# Compute Layer: No-code LLM pipeline composition with budget tracking.
# Ref: AnchoringAI/anchoring-ai — Open-source no-code LLM app builder.

from typing import List, Dict, Optional
import hashlib, math

class PipelineBlock:
    __slots__ = ('name', 'model', 'max_tokens', 'temperature')
    def __init__(self, name: str, model: str, max_tokens: int = 512, temperature: float = 0.7):
        self.name = name
        self.model = model
        self.max_tokens = max(1, max_tokens)
        self.temperature = max(0.0, min(2.0, temperature))

class BudgetTracker:
    __slots__ = ('_limit', '_used')
    def __init__(self, limit: float):
        self._limit = max(0.0, limit)
        self._used = 0.0
    def charge(self, tokens: int, rate: float) -> bool:
        cost = tokens * rate
        if self._used + cost > self._limit:
            return False
        self._used += cost
        return True
    @property
    def remaining(self) -> float:
        return round(self._limit - self._used, 8)

def build_pipeline(blocks: List[PipelineBlock]) -> Dict[str, str]:
    if not blocks:
        return {'error': 'OMNI_ERR: Empty pipeline'}
    raw = ';'.join(f"{b.name}:{b.model}" for b in blocks)
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return {'pipeline_hash': h, 'block_count': str(len(blocks)), 'status': 'READY'}
