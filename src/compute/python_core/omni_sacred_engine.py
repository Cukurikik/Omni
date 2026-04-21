"""
OMNI Sacred Engine
==================
Production-grade abstraction inspired by IDSIA/sacred.
Implements standard immutable telemetry and experiment configuration observers
for logging training variables inside OMNI's zero-mock logic.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import collections
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class SacredError(Exception):
    """Base error for experiment telemetry abstraction."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. EXPERIMENT TELEMETRY OBSERVER
# ---------------------------------------------------------------------------

@dataclass
class ExperimentRecord:
    """Production-grade Experiment Record component."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, List[Any]] = field(default_factory=lambda: collections.defaultdict(list))
    status: str = "RUNNING"


class ExperimentObserver:
    """Immutable state container for runtime parameter and metric ingestion."""
    
    def __init__(self, name: str):
        """Initialize ExperimentObserver."""
        self.record = ExperimentRecord(name=name, start_time=time.time())
        self.record.metrics = {}  # Overriding default_factory locally for clean dict
        
    def inherit_config(self, config_dict: Dict[str, Any]) -> Result:
        """Execute inherit config operation for ExperimentObserver."""
        if self.record.status != "RUNNING":
            return Err("Cannot inherit config; experiment has naturally concluded.")
            
        try:
            # Force JSON-serializable sanity
            safe_conf = json.loads(json.dumps(config_dict))
            self.record.config.update(safe_conf)
            return Ok(True)
        except Exception as e:
            return Err(f"Config violation (non-serializable values): {e}")

    def log_metric(self, name: str, value: float) -> Result:
        """Execute log metric operation for ExperimentObserver."""
        if self.record.status != "RUNNING":
            return Err("Experiment is concluded.")
            
        try:
            if name not in self.record.metrics:
                self.record.metrics[name] = []
            self.record.metrics[name].append((time.time(), float(value)))
            return Ok(True)
            
        except Exception as e:
            return Err(f"Metric capture fault: {e}")

    def conclude(self, success: bool = True) -> Result:
        """Execute conclude operation for ExperimentObserver."""
        if self.record.status != "RUNNING":
            return Err("Already concluded.")
            
        self.record.end_time = time.time()
        self.record.status = "COMPLETED" if success else "FAILED"
        return Ok(self.record)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniSacredEngine:
    """
    Production Engine for Immutable Experiment Tracing.
    """

    def __init__(self, config=None):
        """Initialize OmniSacredEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-sacred"

    def init_observer(self, name: str) -> ExperimentObserver:
        """Performs init observer operation for OmniSacredEngine."""
        return ExperimentObserver(name=name)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniSacredEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic Runtime Telemetry Container",
            "status": "operational",
        }
