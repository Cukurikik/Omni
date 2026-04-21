"""
OMNI Decorator Engine
=====================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from __future__ import annotations

ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI DECORATOR ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : functools + wrapt + Flask decorators + pytest fixtures
# Logic Inherited: Python / Compute Layer (Advanced Decorator Patterns)
# ===========================================================================
#
# By studying Flask and functools, Mother learned decorator patterns:
#   1. functools.wraps preserves __name__, __doc__, __module__
#   2. Decorators with arguments require double nesting
#   3. Class-based decorators implement __call__
#   4. Stacking decorators applies bottom-up
#   5. Descriptor-based decorators for method binding

import functools
import hashlib
import json
import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

F = TypeVar("F", bound=Callable)

logger = logging.getLogger("omni.decorators")


# ============================================================
# PART 1: Timing / Performance Decorators
# ============================================================

def timed(func: F) -> F:
    """Measure execution time of a function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            wrapper._last_duration = elapsed
            wrapper._total_calls += 1
            wrapper._total_time += elapsed

    wrapper._last_duration = 0.0
    wrapper._total_calls = 0
    wrapper._total_time = 0.0
    return wrapper  # type: ignore


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[F], F]:
    """Retry a function on failure with exponential backoff."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    wrapper._total_retries += 1
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception  # type: ignore

        wrapper._total_retries = 0
        return wrapper  # type: ignore

    return decorator


def rate_limit(calls: int, period: float) -> Callable[[F], F]:
    """Limit function calls to `calls` per `period` seconds."""

    def decorator(func: F) -> F:
        timestamps: List[float] = []
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal timestamps
            now = time.time()

            with lock:
                # Remove expired timestamps
                timestamps = [t for t in timestamps if now - t < period]

                if len(timestamps) >= calls:
                    wait_time = period - (now - timestamps[0])
                    if wait_time > 0:
                        time.sleep(wait_time)
                    timestamps = timestamps[1:]

                timestamps.append(time.time())

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


# ============================================================
# PART 2: Caching Decorators
# ============================================================

def memoize(maxsize: int = 128) -> Callable[[F], F]:
    """LRU memoization with cache size limit."""

    def decorator(func: F) -> F:
        cache: OrderedDict = OrderedDict()
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create hashable key
            key = _make_key(args, kwargs)

            with lock:
                if key in cache:
                    cache.move_to_end(key)
                    wrapper._cache_hits += 1
                    return cache[key]

            result = func(*args, **kwargs)

            with lock:
                cache[key] = result
                wrapper._cache_misses += 1
                if len(cache) > maxsize:
                    cache.popitem(last=False)

            return result

        wrapper._cache_hits = 0
        wrapper._cache_misses = 0
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_size = lambda: len(cache)
        return wrapper  # type: ignore

    return decorator


def _make_key(args: tuple, kwargs: dict) -> str:
    """Create a hashable cache key from arguments."""
    key_parts = [repr(a) for a in args]
    key_parts.extend(f"{k}={v!r}" for k, v in sorted(kwargs.items()))
    raw = "|".join(key_parts)
    return hashlib.md5(raw.encode()).hexdigest()


# ============================================================
# PART 3: Validation & Contract Decorators
# ============================================================

def validate_args(**validators: Callable) -> Callable[[F], F]:
    """Validate function arguments by name."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, validator_fn in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator_fn(value):
                        raise ValueError(
                            f"Validation failed for '{param_name}': {value!r}"
                        )

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def deprecated(message: str = "", since: str = "") -> Callable[[F], F]:
    """Mark a function as deprecated with a warning."""
    import warnings

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warn_msg = f"{func.__name__} is deprecated"
            if since:
                warn_msg += f" since {since}"
            if message:
                warn_msg += f": {message}"
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


# ============================================================
# PART 4: Class-Based Decorator (Singleton)
# ============================================================

class singleton:
    """Class decorator that ensures only one instance exists."""

    _instances: Dict[Type, Any] = {}
    _lock = threading.Lock()

    def __init__(self, cls: Type):
        """Initialize singleton."""
        self._cls = cls
        functools.update_wrapper(self, cls)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        with singleton._lock:
            if self._cls not in singleton._instances:
                instance = self._cls(*args, **kwargs)
                singleton._instances[self._cls] = instance
            return singleton._instances[self._cls]

    def __instancecheck__(self, instance: Any) -> bool:
        return isinstance(instance, self._cls)


# ============================================================
# PART 5: Decorator Combinator
# ============================================================

def compose(*decorators: Callable) -> Callable[[F], F]:
    """Compose multiple decorators into one. Applied bottom-up."""

    def combined(func: F) -> F:
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return combined


# ============================================================
# Diagnostics
# ============================================================
