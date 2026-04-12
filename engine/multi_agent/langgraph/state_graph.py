import time
import copy
import operator
from typing import Any

# ==========================================
# 🔀 OMNI MULTI-AGENT: LangGraph — REWRITE MENDALAM (Phase 150)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# Versi sebelumnya SALAH. Saya hanya membuat chain fungsi biasa.
# Setelah membaca dokumentasi resmi LangGraph, saya menyadari bahwa
# INTI SEBENARNYA dari LangGraph adalah:
#
# 1. STATE SCHEMA dengan REDUCERS — bukan dict biasa.
#    Setiap field di state punya "reducer function" yang menentukan
#    BAGAIMANA state di-update ketika node mengembalikan partial update.
#    Contoh: `messages: Annotated[list, operator.add]` berarti messages
#    DITAMBAHKAN (append), bukan di-overwrite.
#    TANPA reducer, nilai baru MENIMPA nilai lama (last-write-wins).
#
# 2. PARTIAL STATE UPDATES — setiap node BUKAN mengembalikan seluruh
#    state, tapi hanya {key: value} yang berubah. Reducer lah yang
#    menentukan bagaimana value baru di-merge ke state existing.
#
# 3. CONDITIONAL EDGES — bukan if-else sederhana, tapi fungsi yang
#    menerima state dan mengembalikan NAMA NODE tujuan berikutnya.
#
# 4. CHECKPOINTING — state disimpan SETELAH setiap node, sehingga
#    jika crash, bisa di-resume dari node terakhir.
#
# 5. INTERRUPT — node bisa menghentikan eksekusi untuk menunggu
#    input manusia (Human-in-the-Loop), lalu dilanjutkan.

# ─────────────────────────────────────────────────
# KOMPONEN 1: State Schema + Reducer System
# ─────────────────────────────────────────────────

class ReducerSpec:
    """Spesifikasi reducer untuk satu field di state."""
    def __init__(self, default_value, reducer_fn=None):
        self.default_value = default_value
        self.reducer_fn = reducer_fn  # None = overwrite (default behavior)

    def apply(self, current_value, new_value):
        """Gabungkan current & new value menggunakan reducer."""
        if self.reducer_fn is None:
            # Default: overwrite (last-write-wins)
            return new_value
        return self.reducer_fn(current_value, new_value)


class StateSchema:
    """
    LangGraph State Schema dengan Reducer Annotations.

    PELAJARAN PENTING:
    - Tanpa reducer → field di-overwrite (last-write-wins).
    - Dengan operator.add pada list → list di-APPEND, bukan di-timpa.
    - Dengan operator.add pada int → integer di-JUMLAHKAN.
    - Custom reducer → developer bisa definisi merge logic sendiri.
    """

    def __init__(self, fields: dict):
        """
        fields = {
            "messages": ReducerSpec([], operator.add),       # APPEND
            "iteration_count": ReducerSpec(0, operator.add),  # SUM
            "status": ReducerSpec("", None),                  # OVERWRITE
            "data": ReducerSpec({}, lambda old, new: {**old, **new}), # MERGE DICT
        }
        """
        self.fields = fields
        self.state = {}
        self._initialize()

    def _initialize(self):
        for key, spec in self.fields.items():
            self.state[key] = copy.deepcopy(spec.default_value)

    def apply_partial_update(self, partial: dict):
        """
        INI YANG SEBENARNYA TERJADI DI LANGGRAPH:
        Node mengembalikan partial dict, dan setiap field
        di-merge ke state menggunakan reducer masing-masing.
        """
        for key, new_value in partial.items():
            if key in self.fields:
                current = self.state[key]
                merged = self.fields[key].apply(current, new_value)
                self.state[key] = merged
            else:
                # Field tidak terdaftar di schema — error di LangGraph asli
                print(f"      ⚠️ [REDUCER] Key '{key}' tidak ada di schema, dilewati.")

    def get(self, key, default=None):
        return self.state.get(key, default)

    def snapshot(self) -> dict:
        return copy.deepcopy(self.state)


# ─────────────────────────────────────────────────
# KOMPONEN 2: Checkpoint Store (Durable Execution)
# ─────────────────────────────────────────────────
class CheckpointStore:
    """
    PELAJARAN: LangGraph menyimpan seluruh state SETELAH setiap node.
    Jika terjadi crash, eksekusi bisa dilanjutkan dari node terakhir.
    Ini yang disebut "durable execution".
    """
    def __init__(self):
        self.checkpoints = []  # [(node_name, state_snapshot, timestamp)]

    def save(self, node_name: str, state_snapshot: dict):
        self.checkpoints.append((node_name, state_snapshot, time.time()))

    def get_last(self):
        return self.checkpoints[-1] if self.checkpoints else None

    def restore(self, index: int) -> dict:
        return copy.deepcopy(self.checkpoints[index][1])

    def count(self):
        return len(self.checkpoints)


# ─────────────────────────────────────────────────
# KOMPONEN 3: Graph Nodes & Edges
# ─────────────────────────────────────────────────
class StateGraph:
    """
    LangGraph StateGraph — VERSI YANG BENAR.
    Setiap node adalah fungsi yang menerima state dan mengembalikan
    PARTIAL UPDATE (bukan seluruh state).
    """

    END = "__END__"

    def __init__(self, schema: StateSchema, name: str = "graph"):
        self.schema = schema
        self.name = name
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry_point = None
        self.interrupt_before = set()  # Nodes yang perlu HITL
        self.checkpoint_store = CheckpointStore()
        print(f"🔀 [LANGGRAPH] StateGraph '{name}' dengan {len(schema.fields)} field schema.")
        for key, spec in schema.fields.items():
            reducer_name = spec.reducer_fn.__name__ if spec.reducer_fn else "overwrite"
            print(f"   📋 {key}: reducer={reducer_name}, default={type(spec.default_value).__name__}")

    def add_node(self, name: str, fn):
        """fn(state_dict) -> partial_update_dict"""
        self.nodes[name] = fn

    def add_edge(self, source: str, target: str):
        self.edges[source] = target

    def add_conditional_edges(self, source: str, condition_fn, mapping: dict):
        """
        condition_fn(state) -> string_key
        mapping = {"approved": "publish", "revision": "writer", ...}
        """
        self.conditional_edges[source] = (condition_fn, mapping)

    def set_entry_point(self, name: str):
        self.entry_point = name

    def set_interrupt_before(self, node_names: list):
        """Human-in-the-Loop: pause sebelum node tertentu."""
        self.interrupt_before = set(node_names)

    def compile(self):
        n_nodes = len(self.nodes)
        n_edges = len(self.edges) + len(self.conditional_edges)
        print(f"   ⚙️ Graph compiled: {n_nodes} nodes, {n_edges} edges, {len(self.interrupt_before)} interrupts")
        return self

    def invoke(self, initial_state: dict = None, max_steps: int = 15) -> dict:
        """Eksekusi graph."""
        if initial_state:
            self.schema.apply_partial_update(initial_state)

        current = self.entry_point
        step = 0

        while current != self.END and step < max_steps:
            step += 1

            # Check interrupt (HITL)
            if current in self.interrupt_before:
                print(f"\n   ⏸️ [INTERRUPT] Node '{current}' membutuhkan persetujuan manusia...")
                print(f"      👤 [HITL] Persetujuan diberikan (simulasi). Melanjutkan.")

            if current not in self.nodes:
                print(f"   ❌ Node '{current}' tidak ditemukan! Berhenti.")
                break

            print(f"\n   ── Step {step}: [{current}] ──")

            # Eksekusi node → mendapat PARTIAL UPDATE
            node_fn = self.nodes[current]
            partial_update = node_fn(self.schema.state)

            # Terapkan partial update menggunakan REDUCERS
            if partial_update:
                print(f"      🔄 [REDUCER] Applying partial update: {list(partial_update.keys())}")
                self.schema.apply_partial_update(partial_update)

            # Checkpoint SETELAH setiap node
            self.checkpoint_store.save(current, self.schema.snapshot())

            # Tentukan node berikutnya
            if current in self.conditional_edges:
                cond_fn, mapping = self.conditional_edges[current]
                decision = cond_fn(self.schema.state)
                next_node = mapping.get(decision, self.END)
                print(f"      🔀 Condition → '{decision}' → next: {next_node}")
                current = next_node
            elif current in self.edges:
                current = self.edges[current]
            else:
                current = self.END

        print(f"\n   🏁 Graph selesai: {step} steps, {self.checkpoint_store.count()} checkpoints")
        return self.schema.state


# ─────────────────────────────────────────────────
# IMPLEMENTASI: Research Report Pipeline
# ─────────────────────────────────────────────────

def researcher_node(state: dict) -> dict:
    """Mengembalikan PARTIAL UPDATE, bukan seluruh state."""
    topic = state.get("topic", "AI")
    findings = [
        f"Fakta 1: {topic} menggunakan graph-based orchestration",
        f"Fakta 2: {topic} mendukung durable execution dengan checkpoints",
        f"Fakta 3: {topic} menggunakan reducer untuk state management",
    ]
    print(f"      🔍 Researcher menemukan {len(findings)} fakta")
    # PARTIAL UPDATE: hanya kembalikan field yang berubah
    return {
        "messages": [{"role": "researcher", "content": f"Ditemukan {len(findings)} fakta"}],
        "findings": findings,
        "iteration_count": 1,  # +1 ke counter (reducer SUM)
        "status": "researched",
    }

def analyst_node(state: dict) -> dict:
    findings = state.get("findings", [])
    insight = f"Insight utama dari {len(findings)} fakta: arsitektur reducer adalah kunci"
    print(f"      📊 Analyst menghasilkan insight")
    return {
        "messages": [{"role": "analyst", "content": insight}],
        "analysis": {"insight": insight, "confidence": 0.91},
        "iteration_count": 1,
        "status": "analyzed",
    }

def writer_node(state: dict) -> dict:
    analysis = state.get("analysis", {})
    findings = state.get("findings", [])
    draft = f"# Laporan\n\n"
    for f in findings:
        draft += f"- {f}\n"
    draft += f"\n## Kesimpulan\n{analysis.get('insight', 'N/A')}\n"
    draft += f"\nKepercayaan: {analysis.get('confidence', 0):.0%}\n"
    print(f"      ✍️ Writer menulis draft ({len(draft)} chars)")
    return {
        "messages": [{"role": "writer", "content": f"Draft selesai ({len(draft)} chars)"}],
        "draft": draft,
        "draft_word_count": len(draft.split()),
        "iteration_count": 1,
        "status": "drafted",
    }

def reviewer_node(state: dict) -> dict:
    word_count = state.get("draft_word_count", 0)
    iteration = state.get("iteration_count", 0)
    if word_count < 10 and iteration < 5:
        decision = "revision"
        feedback = f"Draft terlalu pendek ({word_count} kata). Perbaiki."
        print(f"      🔎 Reviewer: ❌ REVISI ({word_count} kata)")
    else:
        decision = "approved"
        feedback = f"Draft disetujui ({word_count} kata). Kualitas baik."
        print(f"      🔎 Reviewer: ✅ APPROVED ({word_count} kata)")
    return {
        "messages": [{"role": "reviewer", "content": feedback}],
        "review_decision": decision,
        "iteration_count": 1,
        "status": f"review_{decision}",
    }

def publisher_node(state: dict) -> dict:
    print(f"      📢 Publisher: Laporan dipublikasikan!")
    return {
        "messages": [{"role": "publisher", "content": "Laporan berhasil dipublikasikan"}],
        "status": "published",
        "iteration_count": 1,
    }


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🔀 OMNI LANGGRAPH v2 — REWRITE MENDALAM (State + Reducers + HITL)")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Versi lama: State hanya dict biasa, TANPA reducer.")
    print("   SALAH karena: 2 node yang update 'messages' akan saling TIMPA.")
    print("   Versi baru: Setiap field punya REDUCER yang menentukan merge.")
    print("   messages → operator.add (APPEND)")
    print("   iteration_count → operator.add (SUM)")
    print("   status → None (OVERWRITE, last-write-wins)")
    print("   data → lambda merge (DEEP MERGE)")
    print()

    # Definisikan schema DENGAN REDUCERS
    schema = StateSchema({
        "messages":         ReducerSpec([], operator.add),                      # APPEND
        "iteration_count":  ReducerSpec(0, operator.add),                       # SUM
        "status":           ReducerSpec("", None),                              # OVERWRITE
        "topic":            ReducerSpec("", None),                              # OVERWRITE
        "findings":         ReducerSpec([], operator.add),                      # APPEND
        "analysis":         ReducerSpec({}, lambda o, n: {**o, **n}),           # MERGE
        "draft":            ReducerSpec("", None),                              # OVERWRITE
        "draft_word_count": ReducerSpec(0, None),                               # OVERWRITE
        "review_decision":  ReducerSpec("", None),                              # OVERWRITE
    })

    graph = StateGraph(schema, "research_pipeline_v2")
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("publisher", publisher_node)

    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", "reviewer")

    # Conditional edge: reviewer decision → "revision" loops back, "approved" goes forward
    graph.add_conditional_edges(
        "reviewer",
        lambda state: state.get("review_decision", "revision"),
        {"approved": "publisher", "revision": "writer"}
    )
    graph.add_edge("publisher", StateGraph.END)

    # HITL: pause sebelum publish untuk persetujuan manusia
    graph.set_interrupt_before(["publisher"])

    graph.set_entry_point("researcher")
    graph.compile()

    # Jalankan dengan initial state
    final_state = graph.invoke({"topic": "Multi-Agent Systems"})

    # Bukti bahwa REDUCER bekerja
    print(f"\n{'='*70}")
    print("📊 BUKTI REDUCER BEKERJA:")
    print(f"   messages (operator.add): {len(final_state['messages'])} messages TERAKUMULASI:")
    for msg in final_state["messages"]:
        print(f"      [{msg['role']}] {msg['content'][:60]}")
    print(f"   iteration_count (operator.add): {final_state['iteration_count']} (SUM dari setiap node)")
    print(f"   status (overwrite): '{final_state['status']}' (hanya nilai TERAKHIR)")
    print(f"   checkpoints: {graph.checkpoint_store.count()} state snapshots tersimpan")
    print(f"{'='*70}")
