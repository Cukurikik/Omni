"""omni-socket-io-native â€” Task Scheduler"""
import time, heapq
from dataclasses import dataclass, field
from typing import Callable, List

@dataclass(order=True)
class ScheduledTask: priority: int; name: str = field(compare=False); fn: Callable = field(compare=False); interval_ms: int = field(compare=False, default=0)

class TaskScheduler:
    def __init__(self): self.queue: List[ScheduledTask] = []; self.running = False
    def schedule(self, name: str, fn: Callable, priority: int = 0): heapq.heappush(self.queue, ScheduledTask(priority, name, fn))
    def run_next(self):
        if self.queue:
            task = heapq.heappop(self.queue); task.fn(); return task.name
        return None
    def run_all(self):
        results = []
        while self.queue: results.append(self.run_next())
        return results
    def pending(self) -> int: return len(self.queue)