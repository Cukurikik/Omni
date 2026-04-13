import time
import uuid
import math
import random
import re
import json
from enum import Enum
from collections import defaultdict

# ==========================================
# 📊 AGENT MOTHER: GenAI Evaluation + RAG Engine + Tools + Metadata
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ────────────────────────────────────────────────
#
# 1. GENAI EVALUATION — Evaluasi kualitas output LLM/Agent
#    ┌──────────────────────────────────────────────────┐
#    │ VERTEX AI GenAI Evaluation:                       │
#    │                                                    │
#    │ a) AUTOMATIC METRICS (tanpa LLM judge):           │
#    │    - BLEU, ROUGE, METEOR (text similarity)        │
#    │    - Exact Match, F1 Score                        │
#    │    - Perplexity (model confidence)                │
#    │                                                    │
#    │ b) MODEL-BASED METRICS (LLM-as-judge):            │
#    │    - Coherence: apakah logis dan terstruktur?      │
#    │    - Fluency: apakah bahasa natural?               │
#    │    - Safety: apakah aman/tidak toxic?              │
#    │    - Groundedness: apakah berbasis context?        │
#    │    - Fulfillment: apakah menjawab instruksi?      │
#    │                                                    │
#    │ c) PAIRWISE EVALUATION:                            │
#    │    - Model A vs Model B pada pertanyaan yang sama  │
#    │    - Win/Lose/Tie voting                          │
#    │    - ELO rating system                            │
#    │                                                    │
#    │ d) AGENT EVALUATION (khusus agent):                │
#    │    - Tool use accuracy                            │
#    │    - Task completion rate                          │
#    │    - Path efficiency (steps taken)                │
#    │    - Handoff accuracy (multi-agent)                │
#    └──────────────────────────────────────────────────┘
#
# 2. RAG ENGINE (Vertex AI) — Managed RAG pipeline
#    ┌──────────────────────────────────────────────────┐
#    │ Berbeda dari RAG kustom (LlamaIndex):              │
#    │ - Vertex AI RAG Engine = MANAGED service           │
#    │ - Corpus API: create, update, query corpus         │
#    │ - Auto-chunking, auto-embedding (text-embedding-005)│
#    │ - Built-in: Weaviate/Cloud SQL/AlloyDB vector store│
#    │ - Integrated: grounding with Google Search         │
#    │ - Quotas: 10GB/corpus, 100K docs/corpus            │
#    │                                                    │
#    │ API Flow:                                          │
#    │ 1. Create RagCorpus (container)                    │
#    │ 2. Import RagFiles (documents)                     │
#    │ 3. Generate grounded answers via                  │
#    │    GenerateContent + retrievalConfig                │
#    └──────────────────────────────────────────────────┘
#
# 3. TOOLS — Tool registry dan execution layer
#    ┌──────────────────────────────────────────────────┐
#    │ Vertex AI Tool Types:                              │
#    │ a) Function Calling: agent calls your code         │
#    │ b) Extensions: pre-built connectors (Sheets, Ads)  │
#    │ c) Code Interpreter: agent writes + runs code      │
#    │ d) Datastores: RAG knowledge base search           │
#    │ e) Google Search: live web search grounding        │
#    │                                                    │
#    │ FUNCTION CALLING FLOW:                             │
#    │ User → LLM thinks → generates function_call JSON   │
#    │ → YOUR CODE executes → result back to LLM          │
#    │ → LLM generates final response                    │
#    └──────────────────────────────────────────────────┘
#
# 4. METADATA — Track lineage, versioning, artifacts
#    ┌──────────────────────────────────────────────────┐
#    │ Vertex AI ML Metadata:                             │
#    │ - Artifact: data object (dataset, model, endpoint) │
#    │ - Execution: process that creates artifacts        │
#    │ - Context: group related artifacts + executions    │
#    │ - Lineage: DAG of how artifacts were created       │
#    │   Dataset → Training → Model → Evaluation → Deploy│
#    └──────────────────────────────────────────────────┘

# ─────────────────────────────────────────────────
# KOMPONEN 1: GenAI Evaluation Metrics
# ─────────────────────────────────────────────────
class AutomaticMetrics:
    """Automatic text metrics (no LLM judge needed)."""

    @staticmethod
    def rouge_l(reference, candidate):
        """ROUGE-L: Longest Common Subsequence."""
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()
        if not ref_tokens or not cand_tokens:
            return 0.0

        m, n = len(ref_tokens), len(cand_tokens)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref_tokens[i-1] == cand_tokens[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        lcs_len = dp[m][n]
        precision = lcs_len / n if n > 0 else 0
        recall = lcs_len / m if m > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        return round(f1, 4)

    @staticmethod
    def exact_match(reference, candidate):
        return 1.0 if reference.strip().lower() == candidate.strip().lower() else 0.0

    @staticmethod
    def f1_token(reference, candidate):
        ref_tokens = set(reference.lower().split())
        cand_tokens = set(candidate.lower().split())
        common = ref_tokens & cand_tokens
        if not common:
            return 0.0
        precision = len(common) / len(cand_tokens)
        recall = len(common) / len(ref_tokens)
        return round(2 * precision * recall / (precision + recall), 4)


class ModelBasedMetrics:
    """LLM-as-judge metrics (simulated)."""

    CRITERIA = {
        "coherence": "Apakah teks logis, terstruktur, dan mudah diikuti?",
        "fluency": "Apakah bahasa natural dan gramatikal?",
        "safety": "Apakah teks aman, tidak toxic, dan tidak bias?",
        "groundedness": "Apakah jawaban berbasis konteks yang diberikan?",
        "fulfillment": "Apakah jawaban memenuhi instruksi yang diberikan?",
    }

    def evaluate(self, text, context=None, instruction=None):
        scores = {}
        # Heuristic scoring (dalam produksi: LLM judge)
        word_count = len(text.split())
        has_structure = any(c in text for c in [".", ",", ";"])
        has_evidence = context and any(w in text.lower() for w in context.lower().split()[:10])

        scores["coherence"] = min(1.0, 0.3 + 0.1 * min(word_count, 7))
        scores["fluency"] = 0.8 if has_structure else 0.4
        scores["safety"] = 0.95 if not any(w in text.lower() for w in ["bodoh", "jelek", "mati"]) else 0.2
        scores["groundedness"] = 0.85 if has_evidence else 0.3
        scores["fulfillment"] = 0.7 if word_count >= 5 else 0.3

        return {k: round(v, 2) for k, v in scores.items()}


class PairwiseEvaluator:
    """Compare model A vs model B (ELO-style)."""
    def __init__(self):
        self.elo_ratings = defaultdict(lambda: 1000)
        self.match_history = []

    def compare(self, query, response_a, response_b, model_a, model_b, reference=None):
        auto = AutomaticMetrics()
        if reference:
            score_a = auto.rouge_l(reference, response_a)
            score_b = auto.rouge_l(reference, response_b)
        else:
            score_a = len(response_a.split()) / 20.0
            score_b = len(response_b.split()) / 20.0

        if score_a > score_b:
            winner = model_a
        elif score_b > score_a:
            winner = model_b
        else:
            winner = "tie"

        # Update ELO
        if winner != "tie":
            loser = model_b if winner == model_a else model_a
            k = 32
            expected_w = 1 / (1 + 10 ** ((self.elo_ratings[loser] - self.elo_ratings[winner]) / 400))
            self.elo_ratings[winner] += k * (1 - expected_w)
            self.elo_ratings[loser] -= k * (1 - expected_w)

        result = {"query": query[:30], "winner": winner, "score_a": score_a, "score_b": score_b}
        self.match_history.append(result)
        return result


class AgentEvaluator:
    """Evaluate agent-specific capabilities."""
    def evaluate_run(self, trace):
        """Evaluate agent execution trace."""
        total_steps = len(trace)
        tool_uses = [t for t in trace if t.get("event") == "ACT" and "tool" in t]
        thinks = [t for t in trace if t.get("event") == "THINK"]
        handoffs = [t for t in trace if t.get("event") == "HANDOFF"]

        return {
            "total_steps": total_steps,
            "tool_uses": len(tool_uses),
            "thinking_steps": len(thinks),
            "handoffs": len(handoffs),
            "efficiency": round(1 / max(total_steps, 1), 4),  # fewer steps = better
            "tool_use_rate": round(len(tool_uses) / max(total_steps, 1), 4),
        }


# ─────────────────────────────────────────────────
# KOMPONEN 2: Vertex AI RAG Engine (Managed)
# ─────────────────────────────────────────────────
class VertexRAGCorpus:
    """
    PELAJARAN: Vertex AI RAG = managed RAG service.
    Beda dari LlamaIndex:
    - LlamaIndex: kamu manage everything
    - Vertex RAG: Google manage chunking, embedding, storage
    """
    def __init__(self, name, embedding_model="text-embedding-005"):
        self.corpus_id = str(uuid.uuid4())[:8]
        self.name = name
        self.embedding_model = embedding_model
        self.files = []
        self.chunks = []

    def import_files(self, file_paths):
        for fp in file_paths:
            file_obj = {
                "id": str(uuid.uuid4())[:8],
                "path": fp,
                "status": "INDEXED",
                "chunk_count": random.randint(5, 20),
            }
            self.files.append(file_obj)
            # Simulate chunking
            for i in range(file_obj["chunk_count"]):
                self.chunks.append({
                    "file_id": file_obj["id"],
                    "chunk_idx": i,
                    "text": f"Chunk {i} from {fp}",
                    "embedding": [random.gauss(0, 1) for _ in range(256)],
                })
        total_chunks = sum(f["chunk_count"] for f in self.files)
        print(f"      📚 Corpus '{self.name}': {len(self.files)} files, {total_chunks} chunks")

    def query(self, query_text, top_k=3):
        """Retrieve relevant chunks."""
        # Simulate retrieval
        selected = random.sample(self.chunks, min(top_k, len(self.chunks)))
        results = [{"text": c["text"], "score": round(random.uniform(0.5, 0.99), 3),
                    "file_id": c["file_id"]} for c in selected]
        results.sort(key=lambda x: x["score"], reverse=True)
        return results


class VertexRAGEngine:
    """Managed RAG pipeline."""
    def __init__(self):
        self.corpora = {}

    def create_corpus(self, name, embedding_model="text-embedding-005"):
        corpus = VertexRAGCorpus(name, embedding_model)
        self.corpora[name] = corpus
        return corpus

    def generate_grounded_answer(self, corpus_name, query, model="gemini-2.0-flash"):
        corpus = self.corpora[corpus_name]
        results = corpus.query(query)
        context = "\n".join([r["text"] for r in results])
        answer = f"Berdasarkan {len(results)} dokumen: {context[:60]}..."
        return {"answer": answer, "sources": results, "model": model, "grounded": True}


# ─────────────────────────────────────────────────
# KOMPONEN 3: Tool Registry
# ─────────────────────────────────────────────────
class ToolRegistry:
    """
    PELAJARAN: Registry = central catalog semua tools.
    Agent melihat catalog ini untuk MEMUTUSKAN tool mana yang dipanggil.
    """
    def __init__(self):
        self.tools = {}
        self.execution_log = []

    def register(self, name, description, fn, tool_type="function", parameters=None):
        self.tools[name] = {
            "name": name,
            "description": description,
            "fn": fn,
            "type": tool_type,
            "parameters": parameters or {},
            "call_count": 0,
        }

    def list_tools(self):
        return [{"name": t["name"], "description": t["description"], "type": t["type"]}
                for t in self.tools.values()]

    def execute(self, name, **kwargs):
        tool = self.tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        tool["call_count"] += 1
        result = tool["fn"](**kwargs)
        self.execution_log.append({"tool": name, "args": kwargs, "result": str(result)[:50],
                                   "ts": time.time()})
        return result

    def get_schema(self):
        """OpenAPI-compatible schema for function calling."""
        return [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                "parameters": t["parameters"]}} for t in self.tools.values()]


# ─────────────────────────────────────────────────
# KOMPONEN 4: ML Metadata (Lineage Tracking)
# ─────────────────────────────────────────────────
class MLMetadata:
    """
    PELAJARAN: Metadata = lineage tracking.
    Dataset → Training → Model → Evaluation → Deployment
    Setiap node punya type, URI, state.
    """
    def __init__(self):
        self.artifacts = {}
        self.executions = {}
        self.lineage = []

    def create_artifact(self, name, artifact_type, uri, state="LIVE", metadata=None):
        artifact = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "type": artifact_type,
            "uri": uri,
            "state": state,
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        self.artifacts[name] = artifact
        return artifact

    def create_execution(self, name, exec_type, inputs=None, outputs=None):
        execution = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "type": exec_type,
            "inputs": inputs or [],
            "outputs": outputs or [],
            "state": "COMPLETE",
            "created_at": time.time(),
        }
        self.executions[name] = execution

        # Build lineage
        for inp in (inputs or []):
            for out in (outputs or []):
                self.lineage.append({"from": inp, "via": name, "to": out})
        return execution

    def get_lineage(self, artifact_name):
        """Trace lineage for an artifact."""
        chain = []
        current = artifact_name
        for edge in self.lineage:
            if edge["to"] == current:
                chain.append(edge)
                current = edge["from"]
        chain.reverse()
        return chain

    def show_lineage_graph(self):
        """Print lineage as text graph."""
        for edge in self.lineage:
            print(f"      {edge['from']} --[{edge['via']}]--> {edge['to']}")


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("📊 AGENT MOTHER: GenAI Eval + RAG Engine + Tools + Metadata")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   GenAI Eval: ROUGE-L, F1, Model-based (coherence/fluency/safety), Pairwise ELO")
    print("   RAG Engine: Vertex AI managed (Corpus API, auto-chunk, auto-embed)")
    print("   Tools: Function calling, extensions, code interpreter, datastores")
    print("   Metadata: Artifact lineage tracking (Dataset → Model → Deploy)")

    # ── PART 1: GenAI Evaluation ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: GenAI Automatic Metrics")
    auto = AutomaticMetrics()
    ref = "RAG bekerja dengan mencari dokumen relevan dan menggunakannya sebagai konteks"
    cand = "RAG mencari dokumen relevan dari knowledge base lalu menggunakan sebagai konteks untuk LLM"

    print(f"   Reference: '{ref[:50]}...'")
    print(f"   Candidate: '{cand[:50]}...'")
    print(f"   ROUGE-L: {auto.rouge_l(ref, cand)}")
    print(f"   F1 Token: {auto.f1_token(ref, cand)}")
    print(f"   Exact Match: {auto.exact_match(ref, cand)}")

    print(f"\n   Model-Based Metrics (LLM-as-judge):")
    model_metrics = ModelBasedMetrics()
    scores = model_metrics.evaluate(cand, context=ref, instruction="Jelaskan RAG")
    for k, v in scores.items():
        print(f"      {k}: {v}")

    # ── PART 2: Pairwise Evaluation ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: Pairwise Model Comparison (ELO)")
    pairwise = PairwiseEvaluator()

    test_qs = [
        ("Apa itu RAG?", "RAG adalah retrieval augmented generation",
         "RAG mencari dokumen dan menggunakan untuk jawaban", "RAG adalah singkatan dari Retrieval-Augmented Generation"),
        ("Cara kerja embedding?", "Embedding mengubah teks jadi vektor",
         "Embedding model mengkonversi teks menjadi vektor berdimensi tinggi untuk similarity search",
         "Embedding mengubah teks menjadi representasi vektor"),
    ]
    for q, ra, rb, ref_ans in test_qs:
        result = pairwise.compare(q, ra, rb, "gemini-flash", "gemini-pro", ref_ans)
        print(f"   {result['query']}: winner={result['winner']} (A={result['score_a']:.3f}, B={result['score_b']:.3f})")

    print(f"   ELO Ratings: " + ", ".join(f"{m}={int(r)}" for m, r in pairwise.elo_ratings.items()))

    # ── PART 3: RAG Engine ──
    print(f"\n{'─'*60}")
    print("📋 PART 3: Vertex AI RAG Engine")
    rag = VertexRAGEngine()
    corpus = rag.create_corpus("agent_knowledge")
    corpus.import_files(["manual.pdf", "faq.txt", "api_docs.md"])

    answer = rag.generate_grounded_answer("agent_knowledge", "Apa itu fine-tuning?")
    print(f"   Query: 'Apa itu fine-tuning?'")
    print(f"   Answer: {answer['answer'][:60]}...")
    print(f"   Grounded: {answer['grounded']} | Sources: {len(answer['sources'])}")

    # ── PART 4: Tool Registry ──
    print(f"\n{'─'*60}")
    print("📋 PART 4: Tool Registry")
    registry = ToolRegistry()
    registry.register("search_web", "Search the web for information",
                      lambda **kw: {"results": [f"Result for: {kw.get('query', '?')}"]})
    registry.register("execute_python", "Run Python code",
                      lambda **kw: {"output": f"Executed: {kw.get('code', '?')[:30]}"}, tool_type="code_interpreter")
    registry.register("query_database", "Run SQL query",
                      lambda **kw: {"rows": 42, "query": kw.get("sql", "SELECT *")})

    print(f"   Registered tools: {len(registry.list_tools())}")
    for t in registry.list_tools():
        print(f"      🔧 {t['name']} ({t['type']}): {t['description'][:40]}")

    result = registry.execute("search_web", query="Latest AI news")
    print(f"   Executed 'search_web': {result}")

    print(f"\n   Function calling schema:")
    schema = registry.get_schema()
    print(f"   {json.dumps(schema[0], indent=2)[:150]}...")

    # ── PART 5: ML Metadata / Lineage ──
    print(f"\n{'─'*60}")
    print("📋 PART 5: ML Metadata + Lineage")
    meta = MLMetadata()

    meta.create_artifact("agent_sft_v1", "DATASET", "gs://bucket/datasets/sft_v1.jsonl")
    meta.create_artifact("gemini-base", "MODEL", "vertex-ai://models/gemini-2.0-flash")
    meta.create_artifact("agent-tuned-v1", "MODEL", "vertex-ai://models/ft-gemini-abc123")
    meta.create_artifact("eval-report-v1", "METRICS", "gs://bucket/eval/report.json")
    meta.create_artifact("agent-endpoint", "ENDPOINT", "https://agent-abc.run.app")

    meta.create_execution("fine_tuning", "TRAINING", ["agent_sft_v1", "gemini-base"], ["agent-tuned-v1"])
    meta.create_execution("evaluation", "EVALUATION", ["agent-tuned-v1"], ["eval-report-v1"])
    meta.create_execution("deployment", "DEPLOYMENT", ["agent-tuned-v1"], ["agent-endpoint"])

    print("\n   📊 Full Lineage Graph:")
    meta.show_lineage_graph()

    lineage = meta.get_lineage("agent-endpoint")
    print(f"\n   🔗 Lineage for 'agent-endpoint': {len(lineage)} hops")
    for edge in lineage:
        print(f"      {edge['from']} → {edge['to']}")

    print(f"\n{'='*70}")
    print("✅ GenAI Eval + RAG Engine + Tools + Metadata: DIPELAJARI.")
    print("   ROUGE-L + F1 + Exact Match (automatic metrics) ✓")
    print("   LLM-as-judge (coherence/fluency/safety/groundedness) ✓")
    print("   Pairwise ELO (model comparison) ✓")
    print("   Agent evaluator (tool use, efficiency, handoffs) ✓")
    print("   Vertex RAG (Corpus API, auto-chunk, grounded answers) ✓")
    print("   Tool Registry (function calling schema) ✓")
    print("   ML Metadata + Lineage (Dataset→Model→Deploy) ✓")
    print(f"{'='*70}")
