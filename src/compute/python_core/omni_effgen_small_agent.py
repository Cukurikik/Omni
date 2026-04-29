# Omni effGen Small Agent Engine (Python)
# Compute Layer: Enabling small language models as autonomous agents.
# Ref: ctrl-gaurav/effGen — Small LMs as capable autonomous agents.

from typing import List, Dict, Optional

class AgentAction:
    __slots__ = ('action_type', 'target', 'params', 'confidence')
    def __init__(self, action_type: str, target: str, params: Dict, confidence: float):
        self.action_type = action_type
        self.target = target
        self.params = params
        self.confidence = max(0.0, min(1.0, confidence))

def select_action(candidates: List[AgentAction], threshold: float = 0.3) -> Optional[AgentAction]:
    viable = [a for a in candidates if a.confidence >= threshold]
    if not viable: return None
    return max(viable, key=lambda a: a.confidence)

def compute_efficiency_ratio(small_score: float, large_score: float) -> float:
    if large_score <= 0: return 0.0
    return round(small_score / large_score, 6)
