"""
OMNI Context Manager Engine
===========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from __future__ import annotations

ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI CONTEXT MANAGER ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : contextlib + SQLAlchemy session + tempfile + asyncio
# Logic Inherited: Python / Compute Layer (Resource Management via __enter__/__exit__)
# ===========================================================================
#
# By studying contextlib and SQLAlchemy, Mother learned:
#   1. __enter__/__exit__ protocol for deterministic resource cleanup
#   2. contextlib.contextmanager converts generators to context managers
#   3. ExitStack manages dynamic context manager composition
#   4. Async context managers with __aenter__/__aexit__
#   5. Nested context managers via ExitStack

import asyncio
import contextlib
import os
import tempfile
import threading
import time
from contextlib import contextmanager, asynccontextmanager
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


# ============================================================
# PART 1: Transaction Context Manager
# ============================================================

class Transaction:
    """Database-like transaction with commit/rollback semantics."""

    def __init__(self, name: str = "default"):
        """Initialize Transaction."""
        self.name = name
        self._operations: List[Dict[str, Any]] = []
        self._committed = False
        self._rolled_back = False
        self._savepoints: List[int] = []
        self._total_ops = 0

    def execute(self, operation: str, **kwargs: Any) -> None:
        """Record an operation within the transaction."""
        self._operations.append({"op": operation, **kwargs})
        self._total_ops += 1

    def savepoint(self) -> int:
        """Create a savepoint, return its index."""
        sp = len(self._operations)
        self._savepoints.append(sp)
        return sp

    def rollback_to_savepoint(self, sp: int) -> None:
        """Rollback to a savepoint."""
        self._operations = self._operations[:sp]

    def commit(self) -> List[Dict[str, Any]]:
        """Commit all operations."""
        self._committed = True
        return list(self._operations)

    def rollback(self) -> None:
        """Rollback all operations."""
        self._operations.clear()
        self._rolled_back = True

    @property
    def is_active(self) -> bool:
        """Check if active condition holds."""
        return not self._committed and not self._rolled_back

    def __enter__(self) -> "Transaction":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self.rollback()
            return False  # Re-raise exception
        if not self._committed:
            self.commit()
        return False


# ============================================================
# PART 2: Resource Pool Context Manager
# ============================================================

class PooledResource(Generic[T]):
    """Context manager that acquires/releases from a resource pool."""

    def __init__(self, pool: "ResourcePool[T]"):
        """Initialize PooledResource."""
        self._pool = pool
        self._resource: Optional[T] = None

    def __enter__(self) -> T:
        self._resource = self._pool.acquire()
        return self._resource

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._resource is not None:
            self._pool.release(self._resource)
            self._resource = None
        return False


class ResourcePool(Generic[T]):
    """Thread-safe resource pool with context manager support."""

    def __init__(self, factory: Callable[[], T], max_size: int = 10):
        """Initialize ResourcePool."""
        self._factory = factory
        self._max_size = max_size
        self._available: List[T] = []
        self._in_use: List[T] = []
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._total_created = 0
        self._total_acquired = 0
        self._total_released = 0

    def acquire(self) -> T:
        """Acquire a resource, blocking if none available."""
        with self._condition:
            while not self._available and len(self._in_use) >= self._max_size:
                self._condition.wait()

            if self._available:
                resource = self._available.pop()
            else:
                resource = self._factory()
                self._total_created += 1

            self._in_use.append(resource)
            self._total_acquired += 1
            return resource

    def release(self, resource: T) -> None:
        """Release a resource back to the pool."""
        with self._condition:
            if resource in self._in_use:
                self._in_use.remove(resource)
            self._available.append(resource)
            self._total_released += 1
            self._condition.notify()

    def get(self) -> PooledResource[T]:
        """Get a context manager for pool access."""
        return PooledResource(self)

    @property
    def stats(self) -> Dict[str, int]:
        """Execute stats operation for ResourcePool."""
        with self._lock:
            return {
                "available": len(self._available),
                "in_use": len(self._in_use),
                "total_created": self._total_created,
                "total_acquired": self._total_acquired,
                "total_released": self._total_released,
            }


# ============================================================
# PART 3: Timer / Profiler Context Manager
# ============================================================

class Timer:
    """Measure elapsed time within a with-block."""

    def __init__(self, name: str = ""):
        """Initialize Timer."""
        self.name = name
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> bool:
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        return False

    @property
    def elapsed_ms(self) -> float:
        """Execute elapsed ms operation for Timer."""
        return self.elapsed * 1000


# ============================================================
# PART 4: Generator-Based Context Managers
# ============================================================

@contextmanager
def temp_directory(prefix: str = "omni_"):
    """Create and auto-cleanup a temporary directory."""
    dirpath = tempfile.mkdtemp(prefix=prefix)
    try:
        yield dirpath
    finally:
        import shutil
        shutil.rmtree(dirpath, ignore_errors=True)


@contextmanager
def environment_vars(**env_vars: str):
    """Temporarily set environment variables, restore on exit."""
    old_values: Dict[str, Optional[str]] = {}
    for key, value in env_vars.items():
        old_values[key] = os.environ.get(key)
        os.environ[key] = value
    try:
        yield
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


@contextmanager
def suppress_exceptions(*exception_types):
    """Suppress specified exception types silently."""
    try:
        yield
    except exception_types:
        pass


# ============================================================
# PART 5: Async Context Manager
# ============================================================

class AsyncTimer:
    """Async version of Timer."""

    def __init__(self, name: str = ""):
        """Initialize AsyncTimer."""
        self.name = name
        self.elapsed: float = 0.0

    async def __aenter__(self) -> "AsyncTimer":
        self._start = time.perf_counter()
        return self

    async def __aexit__(self, *args: Any) -> bool:
        self.elapsed = time.perf_counter() - self._start
        return False


@asynccontextmanager
async def async_timeout(seconds: float):
    """Async context manager with timeout."""
    try:
        yield await asyncio.wait_for(asyncio.sleep(0), timeout=seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation exceeded {seconds}s timeout")


# ============================================================
# PART 6: Exit Stack Composition
# ============================================================

class ManagedScope:
    """Compose multiple context managers dynamically."""

    def __init__(self):
        """Initialize ManagedScope."""
        self._stack = contextlib.ExitStack()
        self._resources: List[Any] = []
        self._total_managed = 0

    def __enter__(self) -> "ManagedScope":
        self._stack.__enter__()
        return self

    def __exit__(self, *args: Any) -> bool:
        return self._stack.__exit__(*args)

    def enter(self, cm: Any) -> Any:
        """Enter a context manager and track it."""
        resource = self._stack.enter_context(cm)
        self._resources.append(resource)
        self._total_managed += 1
        return resource

    def callback(self, fn: Callable, *args: Any, **kwargs: Any) -> None:
        """Register a cleanup callback."""
        self._stack.callback(fn, *args, **kwargs)


# ============================================================
# Diagnostics
# ============================================================
