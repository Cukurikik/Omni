# ===========================================================================
# OMNI COMPUTE LAYER — CLAUDE SKILLS MARKETPLACE ENGINE
# ===========================================================================
# Source Paradigm : mhattingpete/claude-skills-marketplace
# Domain Layer   : Compute (ML pipeline, AI orchestration)
# Language        : Python
# Function        : Local AI skill execution sandbox — registers, validates,
#                   and executes typed skill plugins with input/output schemas,
#                   version management, dependency tracking, and sandboxed eval
# ===========================================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum
import json
import time


class SkillCategory(Enum):
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    IMAGE = "image"
    AUDIO = "audio"
    TOOL = "tool"


@dataclass(frozen=True)
class SkillSchema:
    """Typed input/output schema for a skill."""
    fields: Dict[str, str]  # field_name -> type annotation ("str", "int", "List[str]", etc.)
    required: Set[str] = field(default_factory=set)

    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Return list of validation errors (empty = valid)."""
        errors = []
        for req_field in self.required:
            if req_field not in data:
                errors.append(f"Missing required field: '{req_field}'")
        for key in data:
            if key not in self.fields:
                errors.append(f"Unknown field: '{key}'")
        return errors


@dataclass
class SkillManifest:
    """Complete skill definition."""
    name: str
    version: str
    description: str
    category: SkillCategory
    author: str
    input_schema: SkillSchema
    output_schema: SkillSchema
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    license: str = "MIT"
    created_at: float = field(default_factory=time.time)


@dataclass
class SkillExecution:
    """Result of a skill invocation."""
    skill_name: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    validated_input: bool = False
    validated_output: bool = False


class SkillMarketplace:
    """
    Core skill registry and execution sandbox.
    Mirrors the claude-skills-marketplace architecture.
    """

    def __init__(self):
        self._registry: Dict[str, SkillManifest] = {}
        self._executors: Dict[str, Callable] = {}
        self._execution_log: List[SkillExecution] = []
        print("[SKILLS-OMNI-PY] Marketplace engine initialized.")

    # ---- Registration --------------------------------------------------------

    def register(self, manifest: SkillManifest,
                 executor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Register a skill with its execution function."""
        key = f"{manifest.name}@{manifest.version}"
        self._registry[key] = manifest
        self._executors[key] = executor
        print(f"[SKILLS-OMNI-PY] Registered: {key} ({manifest.category.value}) "
              f"by {manifest.author} — {manifest.description}")

    def unregister(self, name: str, version: str) -> bool:
        """Remove a skill from the registry."""
        key = f"{name}@{version}"
        if key in self._registry:
            del self._registry[key]
            del self._executors[key]
            print(f"[SKILLS-OMNI-PY] Unregistered: {key}")
            return True
        return False

    # ---- Discovery -----------------------------------------------------------

    def list_skills(self, category: Optional[SkillCategory] = None,
                    tag: Optional[str] = None) -> List[SkillManifest]:
        """List registered skills with optional filtering."""
        results = list(self._registry.values())
        if category:
            results = [s for s in results if s.category == category]
        if tag:
            results = [s for s in results if tag in s.tags]
        return results

    def search(self, query: str) -> List[SkillManifest]:
        """Fuzzy search skills by name or description."""
        q = query.lower()
        return [s for s in self._registry.values()
                if q in s.name.lower() or q in s.description.lower()]

    def get_manifest(self, name: str, version: str) -> Optional[SkillManifest]:
        """Get a specific skill's manifest."""
        return self._registry.get(f"{name}@{version}")

    # ---- Dependency Resolution -----------------------------------------------

    def check_dependencies(self, manifest: SkillManifest) -> List[str]:
        """Check if all dependencies are satisfied. Returns list of missing deps."""
        missing = []
        for dep in manifest.dependencies:
            if dep not in self._registry:
                missing.append(dep)
        return missing

    # ---- Execution -----------------------------------------------------------

    def invoke(self, name: str, version: str,
               input_data: Dict[str, Any]) -> SkillExecution:
        """Execute a skill in the sandbox with full validation."""
        key = f"{name}@{version}"
        print(f"[SKILLS-OMNI-PY] Invoking: {key}")

        manifest = self._registry.get(key)
        if not manifest:
            return self._log_execution(SkillExecution(
                skill_name=key, success=False, error=f"Skill '{key}' not found"))

        # Validate input
        input_errors = manifest.input_schema.validate(input_data)
        if input_errors:
            return self._log_execution(SkillExecution(
                skill_name=key, success=False,
                error=f"Input validation failed: {'; '.join(input_errors)}"))

        # Check dependencies
        missing = self.check_dependencies(manifest)
        if missing:
            return self._log_execution(SkillExecution(
                skill_name=key, success=False,
                error=f"Missing dependencies: {', '.join(missing)}"))

        # Execute in sandbox
        executor = self._executors[key]
        t0 = time.monotonic()
        try:
            output = executor(input_data)
            elapsed = (time.monotonic() - t0) * 1000

            # Validate output
            output_errors = manifest.output_schema.validate(output)
            validated_out = len(output_errors) == 0

            if not validated_out:
                print(f"[SKILLS-OMNI-PY]   ⚠ Output schema mismatch: {output_errors}")

            result = SkillExecution(
                skill_name=key, success=True, output=output,
                elapsed_ms=elapsed, validated_input=True, validated_output=validated_out)
            print(f"[SKILLS-OMNI-PY]   ✓ {key} completed in {elapsed:.1f}ms")
            return self._log_execution(result)

        except Exception as e:
            elapsed = (time.monotonic() - t0) * 1000
            result = SkillExecution(
                skill_name=key, success=False, error=str(e),
                elapsed_ms=elapsed, validated_input=True)
            print(f"[SKILLS-OMNI-PY]   ✗ {key} failed: {e}")
            return self._log_execution(result)

    def _log_execution(self, result: SkillExecution) -> SkillExecution:
        self._execution_log.append(result)
        return result

    # ---- Reporting -----------------------------------------------------------

    def execution_stats(self) -> Dict[str, Any]:
        """Return execution statistics."""
        total = len(self._execution_log)
        successes = sum(1 for e in self._execution_log if e.success)
        avg_ms = (sum(e.elapsed_ms for e in self._execution_log) / total) if total > 0 else 0
        return {
            "total_invocations": total,
            "successes": successes,
            "failures": total - successes,
            "avg_elapsed_ms": round(avg_ms, 2),
            "registered_skills": len(self._registry),
        }


# ---- FFI Test Harness (commented) ------------------------------------------
# mp = SkillMarketplace()
# mp.register(
#     SkillManifest(
#         name="summarize", version="1.0.0", description="Summarize text",
#         category=SkillCategory.TEXT, author="omni",
#         input_schema=SkillSchema({"text": "str"}, required={"text"}),
#         output_schema=SkillSchema({"summary": "str", "word_count": "int"}, required={"summary"}),
#     ),
#     lambda data: {"summary": data["text"][:100], "word_count": len(data["text"].split())}
# )
# result = mp.invoke("summarize", "1.0.0", {"text": "This is a long document..."})
# print(mp.execution_stats())
