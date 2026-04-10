"""omni-velocity-js â€” OMNI Compute Pipeline (Python)"""
from typing import Any, List, Callable, Optional
from dataclasses import dataclass, field
import time

@dataclass
class PipelineStage:
    name: str
    transform: Callable
    timeout_ms: int = 5000

@dataclass
class PipelineResult:
    success: bool
    data: Any = None
    error: str = None
    duration_ms: float = 0.0
    stages_completed: int = 0

class DataPipeline:
    def __init__(self):
        self.stages: List[PipelineStage] = []
        self.middleware: List[Callable] = []

    def add_stage(self, name: str, transform: Callable, timeout_ms: int = 5000):
        self.stages.append(PipelineStage(name, transform, timeout_ms))
        return self

    def use_middleware(self, mw: Callable):
        self.middleware.append(mw)
        return self

    def execute(self, data: Any) -> PipelineResult:
        start = time.time()
        current = data
        completed = 0
        for stage in self.stages:
            try:
                for mw in self.middleware:
                    current = mw(current)
                current = stage.transform(current)
                completed += 1
            except Exception as e:
                return PipelineResult(False, error=f'{stage.name}: {str(e)}', duration_ms=(time.time()-start)*1000, stages_completed=completed)
        return PipelineResult(True, data=current, duration_ms=(time.time()-start)*1000, stages_completed=completed)

    def execute_batch(self, items: List[Any]) -> List[PipelineResult]:
        return [self.execute(item) for item in items]