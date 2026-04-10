"""omni-cockroachdb â€” In-Memory Job Queue"""
from typing import Any, Callable, Optional, List
from collections import deque
from dataclasses import dataclass
from enum import Enum
import time

class JobStatus(Enum): PENDING = 'pending'; RUNNING = 'running'; COMPLETED = 'completed'; FAILED = 'failed'

@dataclass
class Job:
    id: str; fn: Callable; args: tuple = (); status: JobStatus = JobStatus.PENDING; result: Any = None; error: str = None

class JobQueue:
    def __init__(self): self._queue: deque = deque(); self._completed: List[Job] = []; self._failed: List[Job] = []

    def enqueue(self, job: Job): job.status = JobStatus.PENDING; self._queue.append(job)
    def dequeue(self) -> Optional[Job]: return self._queue.popleft() if self._queue else None
    def process_next(self) -> Optional[Job]:
        job = self.dequeue()
        if not job: return None
        job.status = JobStatus.RUNNING
        try: job.result = job.fn(*job.args); job.status = JobStatus.COMPLETED; self._completed.append(job)
        except Exception as e: job.error = str(e); job.status = JobStatus.FAILED; self._failed.append(job)
        return job
    def process_all(self) -> List[Job]:
        results = []
        while self._queue: results.append(self.process_next())
        return results
    def pending(self) -> int: return len(self._queue)
    def stats(self) -> dict: return {'pending': len(self._queue), 'completed': len(self._completed), 'failed': len(self._failed)}