# Omni WKM World Knowledge Planner (Python)
# Compute Layer: Agent planning using world knowledge model for task decomposition.
# Ref: zjunlp/WKM — NeurIPS 2024, Agent Planning with World Knowledge Model.

from typing import List, Dict, Optional
import math

class PlanStep:
    __slots__ = ('action', 'preconditions', 'effects', 'confidence')
    def __init__(self, action: str, preconditions: List[str], effects: List[str], confidence: float):
        self.action = action
        self.preconditions = preconditions
        self.effects = effects
        self.confidence = max(0.0, min(1.0, confidence))

class WorldKnowledgePlanner:
    def __init__(self, knowledge_base: Dict[str, List[str]]):
        self._kb = knowledge_base
        self._plan_cache: Dict[str, List[PlanStep]] = {}

    def decompose_task(self, goal: str, max_depth: int = 10) -> List[PlanStep]:
        if goal in self._plan_cache:
            return self._plan_cache[goal]
        steps: List[PlanStep] = []
        sub_goals = self._kb.get(goal, [])
        if not sub_goals:
            steps.append(PlanStep(goal, [], [goal], 1.0))
        else:
            for i, sg in enumerate(sub_goals[:max_depth]):
                conf = 1.0 / (1.0 + math.log1p(i))
                steps.append(PlanStep(sg, [goal], [sg], round(conf, 6)))
        self._plan_cache[goal] = steps
        return steps

    def evaluate_plan_feasibility(self, steps: List[PlanStep]) -> float:
        if not steps:
            return 0.0
        product = 1.0
        for s in steps:
            product *= s.confidence
        return round(product, 8)
