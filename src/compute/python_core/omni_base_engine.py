"""OmniBaseEngine — Monadic Result type infrastructure for all OMNI engines.

Provides the foundational Result[T, E], Ok(), and Err() types used across
the entire OMNI compute layer for deterministic, exception-free error handling.
"""
from typing import TypeVar, Generic, Union, Any, Dict

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

class Result(Generic[T, E]):
    """Monadic Result type for deterministic error propagation."""
    def __init__(self, value: Union[T, E], is_ok: bool):
        self._value = value
        self._is_ok = is_ok

    def is_ok(self) -> bool:
        """Check if result is Ok."""
        return self._is_ok

    @property
    def value(self):
        """Access wrapped value (Ok path)."""
        return self._value if self._is_ok else None

    @property
    def error(self):
        """Access wrapped error (Err path)."""
        return self._value if not self._is_ok else None

    def unwrap(self) -> T:
        """Unwrap Ok value; raises if Err."""
        if not self._is_ok:
            raise self._value
        return self._value

    def unwrap_err(self) -> E:
        """Unwrap Err value; raises if Ok."""
        if self._is_ok:
            raise Exception("Tried to unwrap_err on an Ok value")
        return self._value

    @staticmethod
    def ok(value: Any) -> 'Result[Any, Any]':
        return Result(value, True)

    @staticmethod
    def fail(error: Any) -> 'Result[Any, Any]':
        return Result(error, False)

def Ok(value: T) -> Result[T, Any]:
    """Construct an Ok result."""
    return Result(value, True)

def Err(error: E) -> Result[Any, E]:
    """Construct an Err result."""
    return Result(error, False)

class OmniBaseEngine:
    """Base class for all OMNI engines."""
    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "capabilities": ["monadic_result"]
        }

def diagnostics() -> Dict[str, Any]:
    """Return base engine metadata for OMNI ecosystem health checks."""
    return {
        "engine": "OmniBaseEngine",
        "version": "1.0.0",
        "status": "operational",
        "layer": "Compute/Infrastructure",
        "capabilities": ["monadic_result", "ok_err_types"],
        "monadic_enforcement": True
    }
