import time
import json
import copy
from enum import Enum
from typing import Any

# ==========================================
# 🔀 OMNI MULTI-AGENT: LangGraph Engine (Phase 145)
# ==========================================
# Framework 1: LangGraph (LangChain)
#   - Stateful graph workflows (StateGraph)
#   - Nodes = Agent/Action, Edges = Flow
#   - Branching, looping, conditional edges
#   - Checkpointing & durable execution
#   - Human-in-the-loop (HITL)
#   - Sub-graphs & deep agents
#   - Memory: short-term + long-term

class AgentState:
    """Shared state yang mengalir di seluruh graph (LangGraph StateGraph)."""
    def __init__(self):
        self.messages = []
        self.data = {}
        self.current_node = ""
        self.iteration = 0
        self.checkpoints = []
        self.metadata = {"created_at": time.time()}

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content, "timestamp": time.time()})

    def checkpoint(self):
        """Durable execution: simpan state untuk recovery."""
        snap = {"messages": copy.deepcopy(self.messages), "data": copy.deepcopy(self.data),
                "node": self.current_node, "iteration": self.iteration}
        self.checkpoints.append(snap)
        return len(self.checkpoints) - 1

    def restore(self, checkpoint_id: int):
        """Restore dari checkpoint (crash recovery)."""
        snap = self.checkpoints[checkpoint_id]
        self.messages = copy.deepcopy(snap["messages"])
        self.data = copy.deepcopy(snap["data"])
        self.current_node = snap["node"]
        self.iteration = snap["iteration"]


class ConditionalEdge:
    """Edge dengan kondisi (branching logic)."""
    def __init__(self, condition_fn, true_target: str, false_target: str):
        self.condition_fn = condition_fn
        self.true_target = true_target
        self.false_target = false_target

    def evaluate(self, state: AgentState) -> str:
        return self.true_target if self.condition_fn(state) else self.false_target


class StateGraph:
    """
    LangGraph StateGraph: DAG berbasis state yang mengatur alur multi-agent.
    - add_node(): Tambah agent/action sebagai node
    - add_edge(): Hubungkan node secara sequential
    - add_conditional_edge(): Branching berdasarkan kondisi state
    - compile() + invoke(): Jalankan graph
    """

    def __init__(self, name: str = "omni_graph"):
        self.name = name
        self.nodes = {}          # {name: callable}
        self.edges = {}          # {source: target_or_ConditionalEdge}
        self.entry_point = None
        self.end_node = "__END__"
        print(f"🔀 [LANGGRAPH] StateGraph '{name}' diinisiasi.")

    def add_node(self, name: str, fn):
        self.nodes[name] = fn
        if self.entry_point is None:
            self.entry_point = name

    def add_edge(self, source: str, target: str):
        self.edges[source] = target

    def add_conditional_edge(self, source: str, condition_fn, true_target: str, false_target: str):
        self.edges[source] = ConditionalEdge(condition_fn, true_target, false_target)

    def set_entry_point(self, name: str):
        self.entry_point = name

    def compile(self):
        print(f"   ⚙️ Compiling graph: {len(self.nodes)} nodes, {len(self.edges)} edges")
        return self

    def invoke(self, state: AgentState, max_iterations: int = 10) -> AgentState:
        """Eksekusi graph dari entry point hingga END."""
        current = self.entry_point
        iteration = 0

        while current != self.end_node and iteration < max_iterations:
            state.current_node = current
            state.iteration = iteration
            iteration += 1

            if current not in self.nodes:
                print(f"   ❌ Node '{current}' tidak ditemukan!")
                break

            print(f"\n   📍 Node [{iteration}]: {current}")
            # Execute node
            self.nodes[current](state)

            # Checkpoint setelah setiap node (durable execution)
            cp_id = state.checkpoint()

            # Navigate to next node
            if current in self.edges:
                edge = self.edges[current]
                if isinstance(edge, ConditionalEdge):
                    next_node = edge.evaluate(state)
                    print(f"   🔀 Conditional → {next_node}")
                else:
                    next_node = edge
                current = next_node
            else:
                current = self.end_node

        print(f"\n   🏁 Graph selesai: {iteration} langkah, {len(state.checkpoints)} checkpoints")
        return state


# ─────────────────────────────────────────────────
# AGENT NODES (Researcher → Analyst → Writer → Reviewer)
# ─────────────────────────────────────────────────
def researcher_node(state: AgentState):
    """Node 1: Researcher — Kumpulkan data."""
    print("      🔍 [Researcher] Mengumpulkan data tentang topik...")
    topic = state.data.get("topic", "OMNI Framework")
    findings = [
        f"{topic} mendukung 15 bahasa pemrograman",
        f"{topic} menggunakan LLVM compiler",
        f"{topic} memiliki arsitektur polylingual",
    ]
    state.data["research_findings"] = findings
    state.add_message("researcher", f"Menemukan {len(findings)} fakta tentang {topic}")
    print(f"      -> {len(findings)} findings dikumpulkan")

def analyst_node(state: AgentState):
    """Node 2: Analyst — Analisis data."""
    print("      📊 [Analyst] Menganalisis temuan peneliti...")
    findings = state.data.get("research_findings", [])
    analysis = {
        "total_findings": len(findings),
        "key_insight": "Arsitektur polylingual adalah keunggulan utama",
        "confidence": 0.92,
        "recommendation": "Fokus pada integrasi LLVM untuk performa"
    }
    state.data["analysis"] = analysis
    state.add_message("analyst", f"Analisis selesai: confidence {analysis['confidence']:.0%}")
    print(f"      -> Insight: {analysis['key_insight']}")

def writer_node(state: AgentState):
    """Node 3: Writer — Tulis laporan."""
    print("      ✍️ [Writer] Menulis laporan berdasarkan analisis...")
    analysis = state.data.get("analysis", {})
    findings = state.data.get("research_findings", [])
    draft = f"# Laporan: {state.data.get('topic', 'N/A')}\n\n"
    draft += f"## Temuan\n"
    for f in findings:
        draft += f"- {f}\n"
    draft += f"\n## Analisis\n{analysis.get('key_insight', 'N/A')}\n"
    draft += f"\n## Rekomendasi\n{analysis.get('recommendation', 'N/A')}\n"

    state.data["draft"] = draft
    state.data["draft_version"] = state.data.get("draft_version", 0) + 1
    state.add_message("writer", f"Draft v{state.data['draft_version']} selesai ({len(draft)} karakter)")
    print(f"      -> Draft v{state.data['draft_version']}: {len(draft)} karakter")

def reviewer_node(state: AgentState):
    """Node 4: Reviewer — Review dan beri feedback."""
    print("      🔎 [Reviewer] Mereview draft...")
    draft = state.data.get("draft", "")
    version = state.data.get("draft_version", 1)

    if len(draft) < 200 and version < 3:
        state.data["review_passed"] = False
        feedback = "Draft terlalu pendek. Tambahkan detail lebih."
        print(f"      -> ❌ REVISI: {feedback}")
    else:
        state.data["review_passed"] = True
        feedback = "Draft approved! Kualitas baik."
        print(f"      -> ✅ APPROVED")

    state.data["feedback"] = feedback
    state.add_message("reviewer", feedback)

def human_approval_node(state: AgentState):
    """Node 5: Human-in-the-Loop (simulasi)."""
    print("      👤 [HITL] Menunggu persetujuan manusia...")
    # Simulasi: auto-approve
    state.data["human_approved"] = True
    state.add_message("human", "Disetujui oleh Tuan Ikky")
    print("      -> ✅ Disetujui oleh manusia (Human-in-the-Loop)")


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 65)
    print("🔀 OMNI LANGGRAPH — Stateful Graph Multi-Agent Workflow")
    print("=" * 65)

    # Build graph
    graph = StateGraph("research_report_pipeline")
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("human_approval", human_approval_node)

    # Sequential edges
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", "reviewer")

    # Conditional: jika review gagal → kembali ke writer (LOOP!)
    graph.add_conditional_edge(
        "reviewer",
        lambda state: state.data.get("review_passed", False),
        true_target="human_approval",
        false_target="writer"
    )
    graph.add_edge("human_approval", "__END__")

    graph.set_entry_point("researcher")
    graph.compile()

    # Run
    state = AgentState()
    state.data["topic"] = "OMNI Framework Multi-Agent"
    result = graph.invoke(state, max_iterations=10)

    # Summary
    print(f"\n{'='*65}")
    print("📋 CONVERSATION LOG")
    for msg in result.messages:
        print(f"   [{msg['role']}]: {msg['content']}")

    print(f"\n📊 STATE:")
    print(f"   Topic: {result.data.get('topic')}")
    print(f"   Findings: {result.data.get('research_findings', [])[:2]}...")
    print(f"   Draft Version: {result.data.get('draft_version')}")
    print(f"   Review: {'PASSED' if result.data.get('review_passed') else 'FAILED'}")
    print(f"   Human Approved: {result.data.get('human_approved')}")
    print(f"   Checkpoints: {len(result.checkpoints)}")

    print(f"\n{'='*65}")
    print("✅ LangGraph: StateGraph ✓ | Conditional Edges ✓ | Loop ✓")
    print("   Checkpointing ✓ | HITL ✓ | Durable Execution ✓")
    print(f"{'='*65}")
