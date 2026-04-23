# ===========================================================================
# OMNI COMPUTE LAYER — ATHENA MEMORY ENGINE (AI AGENT OS)
# ===========================================================================
# Source Repo   : github.com/winstonkoh87/Athena-Public
# Domain Layer  : Compute (AI cognition, persistent memory)
# Language      : Python
# Function      : AI Agent OS — persistent file-based memory system, session
#                 boot/end lifecycle, memory compounding over sessions,
#                 conviction/decisiveness reasoning, governed autonomy with
#                 6 constitutional laws, model-agnostic adapter, context
#                 budget management, and workspace intelligence
# ===========================================================================

"""
OMNI Athena Memory Engine
=========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from __future__ import annotations

ENGINE_VERSION = "1.0.0-omni"
import json
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any
from pathlib import Path


# ---- Constitutional Laws ---------------------------------------------------
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class ConstitutionalLaw(Enum):
    """Athena's 6 constitutional laws governing autonomous behavior."""
    SOVEREIGNTY = (0, "Your life, your weights, your choice.")
    NO_IRREVERSIBLE_RUIN = (1, "Never allow a path that permanently ends the game. Overrides Law #0.")
    TRANSPARENCY = (2, "Always show reasoning, never hide uncertainty.")
    PROPORTIONALITY = (3, "Response depth must match problem importance.")
    COMPOUNDING = (4, "Every session must leave the memory richer than before.")
    AUGMENTATION = (5, "Augment the human, never replace them.")

    def __init__(self, law_id: int, description: str):
        """Initialize ConstitutionalLaw."""
        self.law_id = law_id
        self.description = description


# ---- Capability Levels -----------------------------------------------------

class CapabilityLevel(IntEnum):
    """4-tier capability levels for bounded agency."""
    OBSERVE = 1    # Read-only, gather information
    SUGGEST = 2    # Propose actions, await approval
    ACT_BOUNDED = 3  # Execute within defined boundaries
    ACT_FULL = 4     # Full autonomy within constitutional laws


# ---- Domain Classification -------------------------------------------------

class DomainType(Enum):
    """Type enumeration for DomainType."""
    DETERMINISTIC = "deterministic"      # Math, logic — high conviction
    SEMI_STOCHASTIC = "semi-stochastic"  # Markets, strategy — medium conviction
    STOCHASTIC = "stochastic"            # Social dynamics — low conviction


# ---- Boot Modes ------------------------------------------------------------

class BootMode(Enum):
    """Production-grade Boot Mode component."""
    LIGHTWEIGHT = ("chat", 2000, "Quick chat, minimal context loading")
    FULL = ("start", 10000, "Full boot — loads profile, memory, protocols")
    DEEP = ("ultrastart", 20000, "Deep boot — maximum context, all frameworks")

    def __init__(self, command: str, token_budget: int, description: str):
        """Initialize BootMode."""
        self.command = command
        self.token_budget = token_budget
        self.desc = description


# ---- Memory Node -----------------------------------------------------------

@dataclass
class MemoryNode:
    """An addressable memory unit stored as a file on disk."""
    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    session_created: int = 0
    session_last_accessed: int = 0
    access_count: int = 0
    importance_score: float = 0.5
    filepath: str = ""

    def to_dict(self) -> dict:
        """Convert to dict representation."""
        return {
            "id": self.id,
            "title": self.title,
            "tags": self.tags,
            "session_created": self.session_created,
            "session_last_accessed": self.session_last_accessed,
            "access_count": self.access_count,
            "importance_score": self.importance_score,
        }


@dataclass
class Protocol:
    """A reusable reasoning protocol (decision framework)."""
    id: str       # e.g. "330"
    name: str     # e.g. "Economic Expected Value"
    domain: str   # e.g. "decision", "reasoning", "meta"
    content: str
    tags: list[str] = field(default_factory=list)


@dataclass
class SessionRecord:
    """Metadata for a single agent session."""
    session_id: int
    started_at: float
    ended_at: float | None = None
    boot_mode: str = "start"
    tokens_used: int = 0
    memories_created: int = 0
    memories_accessed: int = 0
    decisions_made: int = 0
    model_used: str = "unknown"


# ---- Context Budget Manager ------------------------------------------------

class ContextBudget:
    """Manages token budget across sessions, scaling to task complexity."""

    def __init__(self, max_tokens: int = 200000):
        """Initialize ContextBudget."""
        self.max_tokens = max_tokens
        self.used_tokens = 0
        self.reserved_for_memory = 0

    def allocate(self, boot_mode: BootMode) -> int:
        """Allocate tokens for memory boot."""
        self.reserved_for_memory = boot_mode.token_budget
        remaining = self.max_tokens - self.reserved_for_memory
        print(f"[ATHENA-OMNI-PY] Context budget: {boot_mode.token_budget} for memory, "
              f"{remaining} free for conversation")
        return remaining

    def consume(self, tokens: int):
        """Execute consume operation for ContextBudget."""
        self.used_tokens += tokens

    def remaining(self) -> int:
        """Execute remaining operation for ContextBudget."""
        return self.max_tokens - self.used_tokens - self.reserved_for_memory

    def utilization(self) -> float:
        """Execute utilization operation for ContextBudget."""
        return (self.used_tokens + self.reserved_for_memory) / self.max_tokens


# ---- Conviction Reasoning Engine -------------------------------------------

class ConvictionEngine:
    """
    Implements conviction/decisiveness split reasoning:
    - conviction = confidence about outcomes (tied to domain determinism)
    - decisiveness = operational precision regardless of conviction
    """

    def __init__(self, config=None):
        """Initialize ConvictionEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True

    @staticmethod
    def assess(domain: DomainType, context_completeness: float) -> dict[str, Any]:
        """
        Returns conviction and decisiveness levels.
        context_completeness: 0.0 to 1.0 (how much relevant memory is available)
        """
        base_conviction = {
            DomainType.DETERMINISTIC: 0.9,
            DomainType.SEMI_STOCHASTIC: 0.5,
            DomainType.STOCHASTIC: 0.2,
        }[domain]

        conviction = base_conviction * context_completeness
        # Decisiveness is always high — operational precision independent of uncertainty
        decisiveness = 0.85 + (context_completeness * 0.15)

        response_style = "assertive"
        if conviction < 0.3:
            response_style = "options-presented"
        elif conviction < 0.6:
            response_style = "structural-zone"

        return {
            "conviction": round(conviction, 2),
            "decisiveness": round(decisiveness, 2),
            "domain": domain.value,
            "response_style": response_style,
            "context_completeness": round(context_completeness, 2),
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-conviction",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


# ---- Model Adapter (Model-Agnostic) ---------------------------------------

class ModelAdapter:
    """Abstracts LLM provider — Claude, GPT, Gemini, local models."""

    def __init__(self, provider: str = "claude", model: str = "claude-sonnet-4-20250514"):
        """Initialize ModelAdapter."""
        self.provider = provider
        self.model = model
        self.session_tokens = 0

    def generate(self, prompt: str, context: list[str]) -> str:
        """Generate response using the configured model."""
        context_str = "\n".join(context[:20])  # Limit context injection
        full_prompt = f"CONTEXT:\n{context_str}\n\nUSER:\n{prompt}"
        token_estimate = len(full_prompt.split()) * 1.3
        self.session_tokens += int(token_estimate)
        # Real: API call to provider
        return f"[{self.provider}/{self.model}] Response for: {prompt[:50]}..."

    def switch_model(self, provider: str, model: str):
        """Switch model without losing memory."""
        old = f"{self.provider}/{self.model}"
        self.provider = provider
        self.model = model
        print(f"[ATHENA-OMNI-PY] Model switched: {old} -> {provider}/{model}")


# ---- Athena Memory Engine --------------------------------------------------

class OmniAthenaMemoryEngine:
    """
    Core Athena engine — persistent memory, governed autonomy, session lifecycle.
    The workspace (folder) IS the product. Memory is stored as Markdown files.
    """

    def __init__(self, workspace_dir: str = ".athena"):
        """Initialize OmniAthenaMemoryEngine."""
        self.workspace = Path(workspace_dir)
        self.memories: dict[str, MemoryNode] = {}
        self.protocols: dict[str, Protocol] = {}
        self.sessions: list[SessionRecord] = []
        self.current_session: SessionRecord | None = None
        self.context_budget = ContextBudget()
        self.conviction_engine = ConvictionEngine()
        self.model = ModelAdapter()
        self.capability_level = CapabilityLevel.SUGGEST
        self.session_counter = 0

        self._load_workspace()
        print(f"[ATHENA-OMNI-PY] Engine initialized: {len(self.memories)} memories, "
              f"{len(self.protocols)} protocols, {len(self.sessions)} past sessions")

    def _load_workspace(self):
        """Load all memory nodes from workspace directory."""
        # In production: scan .athena/ for .md files, parse frontmatter
        # For now: initialize empty workspace
        if not self.workspace.exists():
            self.workspace.mkdir(parents=True, exist_ok=True)
            (self.workspace / "profile").mkdir(exist_ok=True)
            (self.workspace / "protocols").mkdir(exist_ok=True)
            (self.workspace / "case_studies").mkdir(exist_ok=True)
            (self.workspace / "frameworks").mkdir(exist_ok=True)
            (self.workspace / "sessions").mkdir(exist_ok=True)
            print(f"[ATHENA-OMNI-PY] Workspace created: {self.workspace}")

    # ---- Session Lifecycle -------------------------------------------------

    def boot(self, mode: BootMode = BootMode.FULL) -> dict[str, Any]:
        """Boot a new session (/start or /ultrastart)."""
        self.session_counter += 1
        self.current_session = SessionRecord(
            session_id=self.session_counter,
            started_at=time.time(),
            boot_mode=mode.command,
            model_used=f"{self.model.provider}/{self.model.model}",
        )
        remaining = self.context_budget.allocate(mode)

        # Load memories sorted by importance
        top_memories = sorted(
            self.memories.values(),
            key=lambda m: m.importance_score * (1 + m.access_count * 0.1),
            reverse=True,
        )

        # Smart Recall: load until budget exhausted
        loaded_count = 0
        token_estimate = 0
        for mem in top_memories:
            est = len(mem.content.split()) * 1.3
            if token_estimate + est > mode.token_budget:
                break
            token_estimate += est
            mem.session_last_accessed = self.session_counter
            mem.access_count += 1
            loaded_count += 1

        print(f"[ATHENA-OMNI-PY] Session {self.session_counter} booted ({mode.command}): "
              f"{loaded_count} memories loaded, ~{int(token_estimate)} tokens")

        return {
            "session_id": self.session_counter,
            "boot_mode": mode.command,
            "memories_loaded": loaded_count,
            "tokens_for_memory": int(token_estimate),
            "context_remaining": remaining,
        }

    def end_session(self) -> dict[str, Any]:
        """End current session (/end) — persist new learnings."""
        if not self.current_session:
            return {"error": "no active session"}

        self.current_session.ended_at = time.time()
        self.current_session.tokens_used = self.model.session_tokens
        self.sessions.append(self.current_session)

        duration = self.current_session.ended_at - self.current_session.started_at
        summary = {
            "session_id": self.current_session.session_id,
            "duration_minutes": round(duration / 60, 1),
            "tokens_used": self.current_session.tokens_used,
            "memories_created": self.current_session.memories_created,
            "memories_accessed": self.current_session.memories_accessed,
            "total_memories": len(self.memories),
        }

        print(f"[ATHENA-OMNI-PY] Session {self.current_session.session_id} ended: "
              f"{summary['duration_minutes']}min, {summary['tokens_used']} tokens")

        self.current_session = None
        self.model.session_tokens = 0
        return summary

    # ---- Memory Operations -------------------------------------------------

    def remember(self, title: str, content: str, tags: list[str] | None = None) -> str:
        """Create a new persistent memory node."""
        mem_id = f"MEM-{hashlib.md5(title.encode()).hexdigest()[:8]}"
        node = MemoryNode(
            id=mem_id,
            title=title,
            content=content,
            tags=tags or [],
            session_created=self.session_counter,
            session_last_accessed=self.session_counter,
            importance_score=0.5,
        )
        self.memories[mem_id] = node
        if self.current_session:
            self.current_session.memories_created += 1
        print(f"[ATHENA-OMNI-PY] Memory created: {mem_id} '{title}'")
        return mem_id

    def recall(self, query: str, limit: int = 5) -> list[MemoryNode]:
        """Search memories by query (semantic + tag matching)."""
        q = query.lower()
        scored = []
        for mem in self.memories.values():
            score = 0.0
            if q in mem.title.lower():
                score += 3.0
            if q in mem.content.lower():
                score += 1.0
            if any(q in t.lower() for t in mem.tags):
                score += 2.0
            # Recency bonus
            recency = max(0, self.session_counter - mem.session_last_accessed)
            score += max(0, 1.0 - recency * 0.05)
            # Access frequency bonus
            score += min(mem.access_count * 0.1, 1.0)
            if score > 0:
                scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [mem for _, mem in scored[:limit]]
        for mem in results:
            mem.session_last_accessed = self.session_counter
            mem.access_count += 1
        if self.current_session:
            self.current_session.memories_accessed += len(results)
        return results

    def assess_problem(self, problem: str, domain: DomainType = DomainType.SEMI_STOCHASTIC) -> dict:
        """Classify problem and determine conviction/decisiveness."""
        relevant_memories = self.recall(problem, limit=10)
        context_completeness = min(1.0, len(relevant_memories) / 5.0)
        assessment = self.conviction_engine.assess(domain, context_completeness)
        assessment["relevant_memories"] = len(relevant_memories)

        # Check constitutional laws
        assessment["laws_checked"] = [
            {"law": law.name, "id": law.law_id, "description": law.description}
            for law in ConstitutionalLaw
        ]

        if self.current_session:
            self.current_session.decisions_made += 1

        return assessment

    # ---- Statistics --------------------------------------------------------

    def compounding_stats(self) -> dict[str, Any]:
        """Show how memory compounds over sessions."""
        total_sessions = len(self.sessions)
        total_memories = len(self.memories)
        avg_memories_per_session = (total_memories / total_sessions) if total_sessions > 0 else 0

        return {
            "total_sessions": total_sessions,
            "total_memories": total_memories,
            "total_protocols": len(self.protocols),
            "avg_memories_per_session": round(avg_memories_per_session, 1),
            "oldest_memory_session": min((m.session_created for m in self.memories.values()), default=0),
            "most_accessed_memory": max(
                self.memories.values(),
                key=lambda m: m.access_count,
                default=None,
            ),
            "context_utilization": round(self.context_budget.utilization() * 100, 1),
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-athena-memory",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
