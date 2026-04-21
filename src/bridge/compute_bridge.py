# ===========================================================================
# OMNI BRIDGE — COMPUTE ↔ ALL LAYERS INTERFACE
# ===========================================================================
# Python bridge interface for Compute-layer engines. Any compute engine
# (Python, Julia, R, Mojo, Haskell) must satisfy this abstract base class
# to be invocable from UI/Network/Domain layers via the OMNI bridge.
# ===========================================================================

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass(frozen=True)
class ComputeRequest:
    """Canonical payload sent to any compute engine."""
    task_type: str                          # e.g. "predict", "train", "audit"
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_data: Optional[List[float]] = None
    timeout_ms: int = 30000


@dataclass(frozen=True)
class ComputeResponse:
    """Canonical response from any compute engine."""
    result: Any
    metrics: Dict[str, float] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    error: Optional[str] = None

    @property
    def is_ok(self) -> bool:
        return self.error is None


class ComputeBridge(ABC):
    """All compute engines must implement this interface."""

    @abstractmethod
    def execute(self, req: ComputeRequest) -> ComputeResponse:
        """Execute a compute task and return a structured response."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Return the human-readable engine name."""
        ...

    @abstractmethod
    def healthcheck(self) -> bool:
        """Return True if the engine is operational."""
        ...


class NoOpComputeBridge(ComputeBridge):
    """Default no-op implementation for testing."""

    def execute(self, req: ComputeRequest) -> ComputeResponse:
        return ComputeResponse(result=None, elapsed_ms=0.0)

    def name(self) -> str:
        return "noop_compute"

    def healthcheck(self) -> bool:
        return True
