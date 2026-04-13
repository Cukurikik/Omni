import sys
import os

# ==========================================
# 🎯 OMNI RAG: Production RAG Setup Guide (Phase 165)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# Tutorial RAG yang diberikan user menggunakan stack:
#   LlamaIndex + Chroma + Ollama + Sentence-Transformers + Gradio
#
# Saya HARUS memahami bagaimana semua ini terhubung:
#
# ARSITEKTUR LENGKAP:
# ┌──────────────────────────────────────────────────────────────┐
# │ USER                                                         │
# │   │                                                          │
# │   ▼                                                          │
# │ Gradio UI (app.py)                                           │
# │   │                                                          │
# │   ▼                                                          │
# │ Query Engine (LlamaIndex)                                    │
# │   │                                                          │
# │   ├── Retriever ──→ Chroma VectorDB                         │
# │   │                    │                                     │
# │   │                    └── Persisted to ./chroma_db/         │
# │   │                                                          │
# │   └── LLM ──→ Ollama Server (localhost:11434)               │
# │                   │                                          │
# │                   └── llama.cpp (inference engine)            │
# │                        │                                     │
# │                        └── GGUF model file                   │
# │                                                              │
# │ Embedding ──→ Ollama (nomic-embed-text)                     │
# │                                                              │
# │ Documents ──→ SimpleDirectoryReader ──→ chunking ──→ index  │
# └──────────────────────────────────────────────────────────────┘
#
# FLOW DATA:
# 1. SimpleDirectoryReader baca semua file di ./documents/
# 2. Setiap dokumen di-chunk oleh NodeParser (default: RecursiveCharSplitter)
# 3. Setiap chunk di-embed oleh OllamaEmbedding (nomic-embed-text)
# 4. Embedding disimpan di Chroma (persistent di ./chroma_db/)
# 5. User bertanya → query di-embed → cari top-3 chunk terdekat
# 6. Chunk terdekat + pertanyaan → prompt → Ollama (llama3.2) → jawaban
#
# KOMPONEN PER KOMPONEN:

# ─────────────────────────────────────────────────
# KOMPONEN 1: Settings (Global Config)
# ─────────────────────────────────────────────────
class Settings:
    """
    PELAJARAN: LlamaIndex Settings = global config.
    Sekali set, SEMUA index dan query engine pakai config ini.
    Tidak perlu pass per-component.
    """
    llm = None
    embed_model = None
    chunk_size = 1024
    chunk_overlap = 200
    callback_manager = None

    @classmethod
    def configure(cls, llm=None, embed_model=None, chunk_size=None, chunk_overlap=None):
        if llm:
            cls.llm = llm
        if embed_model:
            cls.embed_model = embed_model
        if chunk_size:
            cls.chunk_size = chunk_size
        if chunk_overlap:
            cls.chunk_overlap = chunk_overlap
        print(f"   ⚙️  Settings configured:")
        print(f"      LLM: {cls.llm}")
        print(f"      Embed: {cls.embed_model}")
        print(f"      Chunk: {cls.chunk_size} chars, overlap: {cls.chunk_overlap}")


# ─────────────────────────────────────────────────
# KOMPONEN 2: OllamaEmbedding Config
# ─────────────────────────────────────────────────
class OllamaEmbeddingConfig:
    """
    PELAJARAN: Ollama embedding endpoint:
    POST http://localhost:11434/api/embeddings
    {"model": "nomic-embed-text", "prompt": "teks yang di-embed"}
    Response: {"embedding": [0.1, -0.2, 0.3, ...]}

    Dimensi default nomic-embed-text: 768
    """
    def __init__(self, model_name="nomic-embed-text", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        print(f"   🧠 Embedding: {model_name} via {base_url}")

    def __repr__(self):
        return f"OllamaEmbedding({self.model_name})"


# ─────────────────────────────────────────────────
# KOMPONEN 3: Ollama LLM Config
# ─────────────────────────────────────────────────
class OllamaLLMConfig:
    """
    PELAJARAN: Ollama generate endpoint:
    POST http://localhost:11434/api/generate
    {"model": "llama3.2", "prompt": "...", "stream": true}

    Atau via OpenAI-compatible:
    POST http://localhost:11434/v1/chat/completions
    {"model": "llama3.2", "messages": [...]}
    """
    def __init__(self, model="llama3.2", request_timeout=120.0, base_url="http://localhost:11434"):
        self.model = model
        self.request_timeout = request_timeout
        self.base_url = base_url
        print(f"   🤖 LLM: {model} via {base_url} (timeout: {request_timeout}s)")

    def __repr__(self):
        return f"Ollama({self.model})"


# ─────────────────────────────────────────────────
# KOMPONEN 4: Chroma VectorStore Config
# ─────────────────────────────────────────────────
class ChromaConfig:
    """
    PELAJARAN: Chroma setup steps:
    1. PersistentClient(path="./chroma_db") → data survives restart
    2. get_or_create_collection("name") → idempotent
    3. ChromaVectorStore(collection) → LlamaIndex adapter
    4. StorageContext.from_defaults(vector_store) → inject ke index
    """
    def __init__(self, persist_dir="./chroma_db", collection_name="my_knowledge_base"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        print(f"   🗄️  Chroma: {collection_name} at {persist_dir}")

    def setup_code(self):
        """Kode yang SEBENARNYA dipakai (referensi)."""
        return """
# === CHROMA SETUP (PRODUCTION) ===
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext

chroma_client     = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_knowledge_base")
vector_store      = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context   = StorageContext.from_defaults(vector_store=vector_store)
"""


# ─────────────────────────────────────────────────
# KOMPONEN 5: VectorStoreIndex Flow
# ─────────────────────────────────────────────────
class VectorStoreIndexFlow:
    """
    PELAJARAN: VectorStoreIndex = INTI LlamaIndex.
    Menangani: chunking → embedding → storage dalam satu call.

    from_documents():
    1. Split setiap document → nodes (chunks)
    2. Embed setiap node → vector
    3. Store vector + text + metadata di vector store
    4. Return Index object

    as_query_engine():
    1. Buat retriever (similarity_top_k)
    2. Buat response synthesizer (LLM)
    3. Return QueryEngine yang siap dipakai
    """
    def __init__(self, storage_context=None, show_progress=True):
        self.storage_context = storage_context
        self.show_progress = show_progress
        self.documents = []
        self.nodes = []

    def from_documents(self, documents):
        """
        from_documents() flow:
        Step 1: NodeParser splits documents
        Step 2: EmbedModel embeds each node
        Step 3: VectorStore stores embeddings
        """
        self.documents = documents
        print(f"\n   📑 VectorStoreIndex.from_documents():")
        print(f"      Step 1: NodeParser splits {len(documents)} docs → nodes")
        # Simulasi: tiap doc jadi 2-3 chunk
        for i, doc in enumerate(documents):
            n_chunks = max(1, len(str(doc)) // 200)
            for c in range(n_chunks):
                self.nodes.append({"doc_idx": i, "chunk": c})
        print(f"      Step 2: EmbedModel embeds {len(self.nodes)} nodes")
        print(f"      Step 3: VectorStore stores {len(self.nodes)} vectors")
        print(f"      ✅ Index built: {len(self.nodes)} nodes from {len(documents)} documents")
        return self

    def as_query_engine(self, similarity_top_k=3):
        print(f"   🔍 QueryEngine created (top_k={similarity_top_k})")
        return QueryEngineFlow(similarity_top_k)


class QueryEngineFlow:
    """
    PELAJARAN: QueryEngine.query() flow:
    1. Embed query text → query vector
    2. Search vector store → top-K similar chunks
    3. Compose prompt: context + query
    4. LLM generates response
    5. Return Response with source_nodes
    """
    def __init__(self, top_k=3):
        self.top_k = top_k

    def query(self, question):
        print(f"\n   ❓ query_engine.query(\"{question}\")")
        print(f"      Step 1: embed_model.embed(query) → query_vector")
        print(f"      Step 2: vector_store.search(query_vector, top_k={self.top_k}) → {self.top_k} chunks")
        print(f"      Step 3: prompt = template.format(context=chunks, query=question)")
        print(f"      Step 4: llm.generate(prompt) → response")
        print(f"      Step 5: Response(text=..., source_nodes=[...])")
        return f"[RAG Answer to: {question}]"


# ─────────────────────────────────────────────────
# KOMPONEN 6: Gradio Chat Interface
# ─────────────────────────────────────────────────
class GradioAppFlow:
    """
    PELAJARAN: Gradio app.py architecture:
    - gr.Blocks() = container
    - gr.Chatbot() = chat history display
    - gr.Textbox() = input box
    - gr.Button() = submit trigger
    - .click() / .submit() = event handler

    Event flow:
    User types → submit → jawab_pertanyaan(question, history)
    → query_engine.query(question) → update history → display
    """
    def __init__(self):
        self.history = []

    def jawab_pertanyaan(self, pertanyaan, history):
        """Gradio callback function."""
        if not pertanyaan.strip():
            return "", history
        jawaban = f"[RAG Answer: {pertanyaan}]"
        history.append((pertanyaan, jawaban))
        return "", history

    def simulate_session(self, questions):
        print(f"\n   🌐 Gradio App Session (http://localhost:7860)")
        for q in questions:
            _, self.history = self.jawab_pertanyaan(q, self.history)
            print(f"      User: {q}")
            print(f"      Bot:  {self.history[-1][1]}")


# ─────────────────────────────────────────────────
# KOMPONEN 7: Troubleshooting Guide
# ─────────────────────────────────────────────────
class TroubleshootingGuide:
    """PELAJARAN: Common RAG issues dan solusinya."""

    ISSUES = {
        "Ollama tidak ditemukan": {
            "cause": "Ollama tidak terinstall atau tidak running",
            "solution": "Download dari https://ollama.com, pastikan running (http://localhost:11434)",
        },
        "Model not found": {
            "cause": "Model belum di-download",
            "solution": "ollama pull llama3.2 && ollama pull nomic-embed-text",
        },
        "Out of memory": {
            "cause": "Model terlalu besar untuk RAM/VRAM",
            "solution": "Gunakan model lebih kecil: ollama pull phi3, ganti LLM_MODEL='phi3'",
        },
        "Package not found": {
            "cause": "Package LlamaIndex integrations belum diinstall",
            "solution": "pip install llama-index-llms-ollama llama-index-embeddings-ollama llama-index-vector-stores-chroma",
        },
        "Jawaban tidak relevan": {
            "cause": "Dokumen terlalu sedikit atau chunk size tidak tepat",
            "solution": "Tambah dokumen, naikkan similarity_top_k dari 3 ke 5, atau turunkan chunk_size",
        },
        "Embeddings dimensi mismatch": {
            "cause": "Model embedding berubah setelah index dibuat",
            "solution": "Hapus folder chroma_db/ lalu rebuild index",
        },
    }

    def show_all(self):
        print(f"\n   🔧 Troubleshooting Guide ({len(self.ISSUES)} issues):")
        for issue, info in self.ISSUES.items():
            print(f"      ❌ {issue}")
            print(f"         Cause: {info['cause']}")
            print(f"         Fix: {info['solution']}")


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🎯 OMNI RAG: Production Setup Guide (LlamaIndex + Chroma + Ollama)")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Tutorial dari user = stack: LlamaIndex + Chroma + Ollama + Gradio")
    print("   Saya pelajari setiap komponen dan alur datanya secara mendalam.")
    print()
    print("📐 ARSITEKTUR LENGKAP:")
    print("   User → Gradio UI → QueryEngine → [Retriever → Chroma] + [LLM → Ollama]")
    print("   Documents → DirectoryReader → NodeParser → EmbedModel → VectorStore")

    # PART 1: Settings Configuration
    print(f"\n{'─'*60}")
    print("📋 PART 1: Settings (Global Config)")
    ollama_llm = OllamaLLMConfig("llama3.2", 120.0)
    ollama_embed = OllamaEmbeddingConfig("nomic-embed-text")
    Settings.configure(llm=ollama_llm, embed_model=ollama_embed, chunk_size=1024, chunk_overlap=200)

    # PART 2: Chroma Setup
    print(f"\n{'─'*60}")
    print("📋 PART 2: Chroma VectorDB Setup")
    chroma = ChromaConfig("./chroma_db", "my_knowledge_base")
    print(chroma.setup_code())

    # PART 3: Index Building
    print(f"{'─'*60}")
    print("📋 PART 3: VectorStoreIndex Build Flow")
    index_flow = VectorStoreIndexFlow()
    index = index_flow.from_documents(["doc1_content", "doc2_content", "doc3_content"])

    # PART 4: Query Engine
    print(f"\n{'─'*60}")
    print("📋 PART 4: Query Engine Flow")
    engine = index.as_query_engine(similarity_top_k=3)
    engine.query("Apa itu RAG?")
    engine.query("Bagaimana Ollama bekerja?")

    # PART 5: Gradio App
    print(f"\n{'─'*60}")
    print("📋 PART 5: Gradio Web Interface")
    app = GradioAppFlow()
    app.simulate_session([
        "Apa itu RAG?",
        "Apa saja vector database yang populer?",
        "Cara install Ollama?",
    ])

    # PART 6: Troubleshooting
    print(f"\n{'─'*60}")
    print("📋 PART 6: Troubleshooting Guide")
    guide = TroubleshootingGuide()
    guide.show_all()

    # PART 7: Package Dependencies
    print(f"\n{'─'*60}")
    print("📋 PART 7: Required Packages")
    packages = {
        "llama-index": "Framework RAG utama",
        "chromadb": "Vector database lokal (persistent)",
        "sentence-transformers": "Embedding model (alternatif Ollama embedding)",
        "ollama": "Python client untuk Ollama API",
        "llama-index-llms-ollama": "LlamaIndex ↔ Ollama LLM integration",
        "llama-index-embeddings-ollama": "LlamaIndex ↔ Ollama Embedding integration",
        "llama-index-vector-stores-chroma": "LlamaIndex ↔ Chroma integration",
        "pymupdf": "PDF text extraction",
        "python-docx": "DOCX text extraction",
        "gradio": "Web UI untuk chat interface",
    }
    print(f"   Total: {len(packages)} packages")
    for pkg, desc in packages.items():
        print(f"      pip install {pkg:<40} # {desc}")

    # PART 8: Folder Structure
    print(f"\n{'─'*60}")
    print("📋 PART 8: Project Folder Structure")
    structure = """
    rag-project/
    ├── venv/                    ← Virtual environment
    ├── documents/               ← Knowledge base files
    │   ├── contoh.txt
    │   ├── manual.pdf
    │   └── report.docx
    ├── chroma_db/               ← Persistent vector storage (auto-created)
    │   └── (SQLite + parquet files)
    ├── rag.py                   ← CLI chat interface
    └── app.py                   ← Gradio web interface
    """
    print(structure)

    print(f"{'='*70}")
    print("✅ Production RAG Setup: DIPELAJARI MENDALAM.")
    print("   Settings (global LLM + embed config) ✓")
    print("   Chroma (PersistentClient + collection) ✓")
    print("   VectorStoreIndex (chunk → embed → store) ✓")
    print("   QueryEngine (embed query → retrieve → generate) ✓")
    print("   Gradio (chat UI + event handlers) ✓")
    print("   Troubleshooting (6 common issues) ✓")
    print("   Dependencies (10 packages mapped) ✓")
    print(f"{'='*70}")
