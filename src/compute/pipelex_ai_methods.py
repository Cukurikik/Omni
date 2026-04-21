# ===========================================================================
# OMNI COMPUTE LAYER — PIPELEX AI METHOD PIPELINE ENGINE
# ===========================================================================
# Source Paradigm : Pipelex/pipelex
# Domain Layer   : Compute (ML pipeline, data wrangling, AI orchestration)
# Language        : Python
# Function        : Typed AI procedural pipeline with method chaining,
#                   concept/technique/action schemas, step validation,
#                   and deterministic execution graph for structured AI tasks
# ===========================================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import time
import json


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ConceptSchema:
    """A typed concept definition — the 'what' in Pipelex."""
    name: str
    description: str
    schema_fields: Dict[str, str]  # field_name -> type_hint

    def validate(self, data: Dict[str, Any]) -> bool:
        """Check that data satisfies the concept schema."""
        for field_name in self.schema_fields:
            if field_name not in data:
                return False
        return True


@dataclass(frozen=True)
class Technique:
    """A technique definition — the 'how' in Pipelex."""
    name: str
    input_concept: str
    output_concept: str
    method: str  # "llm_generate", "transform", "validate", "aggregate"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineStep:
    """A single step in the execution graph."""
    step_id: str
    technique: Technique
    status: StepStatus = StepStatus.PENDING
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    retry_count: int = 0

    def is_terminal(self) -> bool:
        return self.status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED)


class PipelexEngine:
    """
    Core pipeline execution engine. Manages concept registry,
    technique library, and deterministic step-by-step execution.
    """

    MAX_RETRIES = 3

    def __init__(self):
        self._concepts: Dict[str, ConceptSchema] = {}
        self._techniques: Dict[str, Technique] = {}
        self._executors: Dict[str, Callable] = {}
        self._steps: List[PipelineStep] = []
        print("[PIPELEX-OMNI-PY] Engine initialized.")

    # ---- Registration --------------------------------------------------------

    def register_concept(self, concept: ConceptSchema) -> None:
        """Register a typed concept into the schema registry."""
        self._concepts[concept.name] = concept
        print(f"[PIPELEX-OMNI-PY] Registered concept: {concept.name} ({len(concept.schema_fields)} fields)")

    def register_technique(self, technique: Technique,
                           executor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Register a technique with its execution function."""
        self._techniques[technique.name] = technique
        self._executors[technique.name] = executor
        print(f"[PIPELEX-OMNI-PY] Registered technique: {technique.name} ({technique.method})")

    # ---- Pipeline Construction -----------------------------------------------

    def add_step(self, step_id: str, technique_name: str) -> PipelexEngine:
        """Add a step to the pipeline (method chaining)."""
        technique = self._techniques.get(technique_name)
        if technique is None:
            raise ValueError(f"Technique '{technique_name}' not registered.")
        self._steps.append(PipelineStep(step_id=step_id, technique=technique))
        return self

    # ---- Execution -----------------------------------------------------------

    def execute(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the entire pipeline sequentially."""
        print(f"[PIPELEX-OMNI-PY] Executing pipeline with {len(self._steps)} step(s)...")
        current_data = initial_data

        for step in self._steps:
            # Validate input concept
            input_concept = self._concepts.get(step.technique.input_concept)
            if input_concept and not input_concept.validate(current_data):
                step.status = StepStatus.FAILED
                step.error = f"Input validation failed for concept '{step.technique.input_concept}'"
                print(f"[PIPELEX-OMNI-PY]   ✗ Step '{step.step_id}': {step.error}")
                continue

            step.input_data = current_data
            step.status = StepStatus.RUNNING

            # Execute with retry
            executor = self._executors.get(step.technique.name)
            success = False
            while step.retry_count <= self.MAX_RETRIES and not success:
                try:
                    t0 = time.monotonic()
                    result = executor(current_data)
                    step.elapsed_ms = (time.monotonic() - t0) * 1000
                    step.output_data = result
                    step.status = StepStatus.COMPLETED
                    current_data = result
                    success = True
                    print(f"[PIPELEX-OMNI-PY]   ✓ Step '{step.step_id}' completed in {step.elapsed_ms:.1f}ms")
                except Exception as e:
                    step.retry_count += 1
                    step.error = str(e)
                    if step.retry_count > self.MAX_RETRIES:
                        step.status = StepStatus.FAILED
                        print(f"[PIPELEX-OMNI-PY]   ✗ Step '{step.step_id}' failed after {self.MAX_RETRIES} retries: {e}")

            # Validate output concept
            if step.status == StepStatus.COMPLETED:
                output_concept = self._concepts.get(step.technique.output_concept)
                if output_concept and not output_concept.validate(current_data):
                    step.status = StepStatus.FAILED
                    step.error = f"Output validation failed for concept '{step.technique.output_concept}'"
                    print(f"[PIPELEX-OMNI-PY]   ✗ Step '{step.step_id}': {step.error}")

        total_ms = sum(s.elapsed_ms for s in self._steps)
        completed = sum(1 for s in self._steps if s.status == StepStatus.COMPLETED)
        print(f"[PIPELEX-OMNI-PY] Pipeline finished: {completed}/{len(self._steps)} steps OK ({total_ms:.1f}ms total)")

        return current_data

    # ---- Reporting -----------------------------------------------------------

    def report(self) -> str:
        """Generate a JSON execution report."""
        return json.dumps([
            {
                "step": s.step_id,
                "technique": s.technique.name,
                "status": s.status.value,
                "elapsed_ms": round(s.elapsed_ms, 2),
                "error": s.error,
            }
            for s in self._steps
        ], indent=2)


# ---- FFI Test Harness (commented) ------------------------------------------
# engine = PipelexEngine()
# engine.register_concept(ConceptSchema("RawText", "Unprocessed text", {"text": "str"}))
# engine.register_concept(ConceptSchema("Summary", "Summarized text", {"summary": "str", "word_count": "int"}))
# engine.register_technique(
#     Technique("summarize", "RawText", "Summary", "llm_generate"),
#     lambda data: {"summary": data["text"][:50] + "...", "word_count": len(data["text"].split())}
# )
# engine.add_step("step-1", "summarize")
# result = engine.execute({"text": "This is a long document that needs summarization."})
# print(engine.report())
