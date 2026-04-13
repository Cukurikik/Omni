import math
import re
import time
import random
import hashlib
from collections import defaultdict, Counter

# ==========================================
# 🧠 OMNI RAG: Embedding + VectorStore + QueryEngine (Phase 164)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# Ini adalah JANTUNG dari RAG. Setelah dokumen di-chunk,
# setiap chunk harus melalui pipeline ini:
#
# 1. EMBEDDING — teks → vektor berdimensi tinggi
#    Model: sentence-transformers, nomic-embed-text, OpenAI ada-002
#    Cara kerja: model neural network yang sudah trained pada
#    jutaan pasangan teks serupa → teks yang MIRIP secara
#    MAKNA akan memiliki vektor yang DEKAT.
#    Dimensi: 384 (MiniLM), 768 (BERT), 1536 (OpenAI)
#
# 2. VECTOR STORE — simpan dan cari embedding
#    Insert: id + vector + metadata
#    Search: query_vector → top-K nearest neighbors
#    Metric: cosine similarity, dot product, L2 distance
#
# 3. RETRIEVER — ambil top-K chunks relevan
#    - Dense retrieval: vector similarity
#    - Sparse retrieval: BM25 keyword matching
#    - Hybrid: combine both (Weaviate, Qdrant)
#    - Re-ranking: ambil top-20, lalu model re-rank jadi top-5
#
# 4. QUERY ENGINE — retriever + LLM = jawaban
#    Retrieve top-K context → inject ke prompt → LLM generate

# ─────────────────────────────────────────────────
# KOMPONEN 1: Embedding Model (TF-IDF + Semantic)
# ─────────────────────────────────────────────────
class TFIDFEmbedding:
    """
    PELAJARAN: TF-IDF = "sparse embedding" klasik.
    TF = term frequency (seberapa sering kata muncul di dokumen)
    IDF = inverse document frequency (seberapa langka kata di seluruh corpus)
    TF × IDF = kata yang sering di DOKUMEN INI tapi langka di corpus
    → nilai tinggi = kata PENTING untuk dokumen ini.
    """
    def __init__(self):
        self.vocabulary = {}
        self.idf_scores = {}
        self.doc_count = 0

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def fit(self, documents):
        """Build vocabulary dan hitung IDF dari corpus."""
        self.doc_count = len(documents)
        doc_freq = defaultdict(int)
        all_tokens = set()

        for doc in documents:
            tokens = set(self._tokenize(doc))
            all_tokens.update(tokens)
            for token in tokens:
                doc_freq[token] += 1

        # Build vocab
        for i, token in enumerate(sorted(all_tokens)):
            self.vocabulary[token] = i

        # IDF: log(N / df)
        for token, df in doc_freq.items():
            self.idf_scores[token] = math.log(self.doc_count / (df + 1)) + 1

        print(f"      TF-IDF fitted: {len(self.vocabulary)} terms, {self.doc_count} docs")

    def embed(self, text):
        """Convert text → sparse TF-IDF vector."""
        tokens = self._tokenize(text)
        tf = Counter(tokens)
        vector = [0.0] * len(self.vocabulary)

        for token, freq in tf.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                tf_score = freq / len(tokens) if tokens else 0
                idf_score = self.idf_scores.get(token, 1.0)
                vector[idx] = tf_score * idf_score

        # Normalize (L2 norm)
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        return vector

    @property
    def dimension(self):
        return len(self.vocabulary)


class DenseEmbedding:
    """
    PELAJARAN: Dense embedding (sentence-transformers style).
    Dalam realita, ini adalah neural network.
    Saya simulasikan dengan hash-based projection yang
    menghasilkan representasi semantik deterministik.
    """
    def __init__(self, dim=64):
        self.dim = dim

    def embed(self, text):
        """Hash-based semantic projection (deterministic)."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        vector = [0.0] * self.dim

        for i, token in enumerate(tokens):
            # Hash token ke dimensi
            h = hashlib.md5(token.encode()).hexdigest()
            for j in range(self.dim):
                char_idx = j % len(h)
                val = (int(h[char_idx], 16) - 8) / 8.0
                # Position-aware weighting
                weight = 1.0 / (1.0 + abs(i - len(tokens) / 2) * 0.1)
                vector[j] += val * weight

        # Normalize
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        return vector

    @property
    def dimension(self):
        return self.dim


class OllamaEmbedding:
    """
    PELAJARAN: Ollama embedding model (nomic-embed-text).
    Dalam realita: POST http://localhost:11434/api/embeddings
    Request: {"model": "nomic-embed-text", "prompt": "text"}
    Response: {"embedding": [0.1, -0.2, ...]}

    Saya simulasikan dengan DenseEmbedding.
    """
    def __init__(self, model_name="nomic-embed-text", dim=64):
        self.model_name = model_name
        self.backend = DenseEmbedding(dim)

    def embed(self, text):
        return self.backend.embed(text)

    @property
    def dimension(self):
        return self.backend.dim


# ─────────────────────────────────────────────────
# KOMPONEN 2: Vector Store (Chroma-style)
# ─────────────────────────────────────────────────
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def bm25_score(query_tokens, doc_tokens, avg_doc_len, total_docs, doc_freq):
    k1, b = 1.2, 0.75
    score = 0.0
    doc_len = len(doc_tokens)
    for token in query_tokens:
        tf = doc_tokens.count(token)
        df = doc_freq.get(token, 1)
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_len / max(avg_doc_len, 1)))
        score += idf * (numerator / denominator)
    return score


class ChromaVectorStore:
    """
    PELAJARAN: Chroma architecture:
    - Collection = container untuk embeddings (seperti SQL table)
    - Persistent mode: SQLite + disk storage
    - get_or_create_collection: idempotent
    - add: batch insert (ids, embeddings, documents, metadatas)
    - query: top-K nearest neighbors
    """
    def __init__(self, collection_name="default"):
        self.collection_name = collection_name
        self.entries = []  # [{id, vector, document, metadata}]
        self.doc_freq = defaultdict(int)

    def add(self, doc_id, vector, document, metadata=None):
        entry = {"id": doc_id, "vector": vector, "document": document, "metadata": metadata or {}}
        self.entries.append(entry)
        for token in set(document.lower().split()):
            self.doc_freq[token] += 1

    def query_vector(self, query_vector, top_k=3, filter_metadata=None):
        """Dense vector search (cosine similarity)."""
        results = []
        for entry in self.entries:
            if filter_metadata:
                skip = any(entry["metadata"].get(k) != v for k, v in filter_metadata.items())
                if skip:
                    continue
            score = cosine_similarity(query_vector, entry["vector"])
            results.append({**entry, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def query_hybrid(self, query_vector, query_text, top_k=3, alpha=0.7):
        """Hybrid search: alpha * vector + (1-alpha) * BM25."""
        query_tokens = query_text.lower().split()
        avg_doc_len = sum(len(e["document"].split()) for e in self.entries) / max(len(self.entries), 1)
        total_docs = len(self.entries)

        results = []
        for entry in self.entries:
            vec_score = cosine_similarity(query_vector, entry["vector"])
            kw_score = bm25_score(query_tokens, entry["document"].lower().split(),
                                  avg_doc_len, total_docs, self.doc_freq)
            combined = alpha * vec_score + (1 - alpha) * kw_score
            results.append({**entry, "vec_score": vec_score, "bm25_score": kw_score, "score": combined})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def count(self):
        return len(self.entries)


# ─────────────────────────────────────────────────
# KOMPONEN 3: Retriever
# ─────────────────────────────────────────────────
class VectorRetriever:
    """Dense retriever — pure vector similarity."""
    def __init__(self, vector_store, embed_model, top_k=3):
        self.store = vector_store
        self.embed_model = embed_model
        self.top_k = top_k

    def retrieve(self, query_text):
        query_vec = self.embed_model.embed(query_text)
        results = self.store.query_vector(query_vec, self.top_k)
        return results


class HybridRetriever:
    """Hybrid retriever — vector + BM25."""
    def __init__(self, vector_store, embed_model, top_k=3, alpha=0.7):
        self.store = vector_store
        self.embed_model = embed_model
        self.top_k = top_k
        self.alpha = alpha

    def retrieve(self, query_text):
        query_vec = self.embed_model.embed(query_text)
        results = self.store.query_hybrid(query_vec, query_text, self.top_k, self.alpha)
        return results


# ─────────────────────────────────────────────────
# KOMPONEN 4: Prompt Template
# ─────────────────────────────────────────────────
class PromptTemplate:
    """
    PELAJARAN: RAG prompt = instruksi + konteks + pertanyaan.
    Template ini yang LlamaIndex/LangChain gunakan secara internal.
    """
    DEFAULT_TEMPLATE = """Berdasarkan konteks berikut, jawab pertanyaan dengan akurat.
Jika jawaban tidak ada di konteks, katakan "Saya tidak menemukan informasi tersebut."

Konteks:
{context}

Pertanyaan: {query}

Jawaban:"""

    def __init__(self, template=None):
        self.template = template or self.DEFAULT_TEMPLATE

    def format(self, context, query):
        return self.template.format(context=context, query=query)


# ─────────────────────────────────────────────────
# KOMPONEN 5: LLM (Simulated Local)
# ─────────────────────────────────────────────────
class LocalLLM:
    """
    PELAJARAN: Dalam produksi, ini memanggil Ollama API:
    POST http://localhost:11434/api/generate
    {"model": "llama3.2", "prompt": "...", "stream": false}

    Saya simulasikan dengan context-aware response generation.
    """
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name

    def generate(self, prompt, temperature=0.7):
        # Extract context dan query dari prompt
        context_match = re.search(r'Konteks:\n(.+?)\n\nPertanyaan:', prompt, re.DOTALL)
        query_match = re.search(r'Pertanyaan: (.+?)\n', prompt)

        context = context_match.group(1) if context_match else ""
        query = query_match.group(1) if query_match else ""

        # Context-aware response (simulasi)
        query_lower = query.lower()
        context_sentences = re.split(r'[.!?]\s+', context)
        relevant = []

        query_words = set(re.findall(r'\b\w+\b', query_lower))
        for sent in context_sentences:
            sent_words = set(re.findall(r'\b\w+\b', sent.lower()))
            overlap = len(query_words & sent_words)
            if overlap >= 2 or any(w in sent.lower() for w in query_words if len(w) > 3):
                relevant.append(sent.strip())

        if relevant:
            response = "Berdasarkan konteks yang diberikan: " + ". ".join(relevant[:3]) + "."
        else:
            response = "Saya tidak menemukan informasi yang cukup spesifik untuk menjawab pertanyaan tersebut berdasarkan konteks yang diberikan."

        return response


# ─────────────────────────────────────────────────
# KOMPONEN 6: Query Engine (INTI RAG)
# ─────────────────────────────────────────────────
class RAGQueryEngine:
    """
    PELAJARAN KUNCI:
    Query Engine = Retriever + LLM + Prompt Template.
    Ini adalah INTI dari RAG — SATU function call yang:
    1. Encode query → embedding
    2. Retrieve top-K context dari vector store
    3. Format prompt dengan context + query
    4. Generate jawaban dari LLM
    5. Return jawaban + source attribution
    """
    def __init__(self, retriever, llm, prompt_template=None):
        self.retriever = retriever
        self.llm = llm
        self.prompt_template = prompt_template or PromptTemplate()

    def query(self, question):
        print(f"\n   ❓ Query: \"{question}\"")

        # Step 1: Retrieve relevant context
        results = self.retriever.retrieve(question)
        print(f"   🔍 Retrieved {len(results)} chunks:")
        for i, r in enumerate(results):
            score = r.get("score", r.get("vec_score", 0))
            print(f"      [{i+1}] score={score:.4f} | {r['metadata'].get('source', '?')} | '{r['document'][:50]}...'")

        # Step 2: Build context string
        context_parts = []
        sources = set()
        for r in results:
            context_parts.append(r["document"])
            sources.add(r["metadata"].get("source", "unknown"))
        context = "\n---\n".join(context_parts)

        # Step 3: Format prompt
        prompt = self.prompt_template.format(context=context, query=question)

        # Step 4: Generate answer
        answer = self.llm.generate(prompt)
        print(f"   💡 Answer: {answer[:100]}...")
        print(f"   📚 Sources: {', '.join(sources)}")

        return {
            "answer": answer,
            "sources": list(sources),
            "context_chunks": len(results),
            "query": question,
        }


# ─────────────────────────────────────────────────
# KOMPONEN 7: Full RAG Pipeline (end-to-end)
# ─────────────────────────────────────────────────
class RAGPipeline:
    """
    Full RAG pipeline: Document → Chunk → Embed → Store → Retrieve → Generate.
    Replika arsitektur LlamaIndex VectorStoreIndex.
    """
    def __init__(self, embed_model=None, llm=None, chunk_size=300, chunk_overlap=50):
        self.embed_model = embed_model or DenseEmbedding(dim=64)
        self.llm = llm or LocalLLM()
        self.vector_store = ChromaVectorStore("rag_knowledge")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Lazy import to avoid circular
        from document_loader import RecursiveCharacterSplitter
        self.splitter = RecursiveCharacterSplitter(chunk_size, chunk_overlap)

    def ingest(self, documents):
        """Ingest documents: chunk → embed → store."""
        print(f"\n📥 [INGEST] Processing {len(documents)} documents...")

        # Chunk
        nodes = self.splitter.split_documents(documents)
        print(f"   Chunks: {len(nodes)}")

        # Embed + Store
        for node in nodes:
            embedding = self.embed_model.embed(node.text)
            self.vector_store.add(node.doc_id, embedding, node.text, node.metadata)

        print(f"   Stored: {self.vector_store.count()} vectors")
        return nodes

    def as_query_engine(self, top_k=3, mode="hybrid"):
        """Create query engine (LlamaIndex style)."""
        if mode == "hybrid":
            retriever = HybridRetriever(self.vector_store, self.embed_model, top_k)
        else:
            retriever = VectorRetriever(self.vector_store, self.embed_model, top_k)
        return RAGQueryEngine(retriever, self.llm)


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    # Import document_loader dari same directory
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.')
    from document_loader import Document, SimpleDirectoryReader, RecursiveCharacterSplitter

    print("=" * 70)
    print("🧠 OMNI RAG: Complete Pipeline — Embed → Store → Retrieve → Generate")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Embedding: TF-IDF (sparse) + Dense (hash-projection, simulated neural)")
    print("   VectorStore: Chroma-style (collection + cosine + hybrid BM25)")
    print("   Retriever: Dense (vector-only) + Hybrid (vector + BM25)")
    print("   QueryEngine: Retriever + PromptTemplate + LLM → answer + sources")
    print("   Pipeline: Document → Chunk → Embed → Store → Retrieve → Generate")

    # ── PART 1: Embedding Models ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: Embedding Models")

    texts = [
        "RAG menggunakan retrieval untuk augment LLM",
        "Vector database menyimpan embedding",
        "Python adalah bahasa pemrograman populer",
    ]

    # TF-IDF
    tfidf = TFIDFEmbedding()
    tfidf.fit(texts)
    for text in texts:
        vec = tfidf.embed(text)
        nonzero = sum(1 for v in vec if v > 0)
        print(f"   TF-IDF: '{text[:35]}...' → dim={len(vec)}, nonzero={nonzero}")

    # Dense
    dense = DenseEmbedding(dim=64)
    for text in texts:
        vec = dense.embed(text)
        print(f"   Dense:  '{text[:35]}...' → dim={len(vec)}, norm={math.sqrt(sum(v*v for v in vec)):.4f}")

    # Similarity check
    v1 = dense.embed("RAG menggunakan retrieval")
    v2 = dense.embed("Retrieval augmented generation")
    v3 = dense.embed("Kucing suka makan ikan")
    print(f"\n   Similarity (RAG ↔ Retrieval): {cosine_similarity(v1, v2):.4f} ← SHOULD be HIGH")
    print(f"   Similarity (RAG ↔ Kucing):    {cosine_similarity(v1, v3):.4f} ← SHOULD be LOW")

    # ── PART 2: Vector Store ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: Vector Store (Chroma-style)")
    store = ChromaVectorStore("test_collection")

    # Load documents + embed
    reader = SimpleDirectoryReader("./nonexistent")
    documents = reader.load_data()
    splitter = RecursiveCharacterSplitter(chunk_size=200, chunk_overlap=30)
    nodes = splitter.split_documents(documents)

    for node in nodes:
        vec = dense.embed(node.text)
        store.add(node.doc_id, vec, node.text, node.metadata)
    print(f"   Stored: {store.count()} vectors")

    # ── PART 3: Retrieval ──
    print(f"\n{'─'*60}")
    print("📋 PART 3: Retrieval (Dense + Hybrid)")

    print("\n   🔍 Dense retrieval: 'apa itu RAG?'")
    dense_ret = VectorRetriever(store, dense, top_k=3)
    results = dense_ret.retrieve("apa itu RAG?")
    for r in results:
        print(f"      score={r['score']:.4f} | {r['metadata'].get('source', '?')}: '{r['document'][:50]}...'")

    print("\n   🔍 Hybrid retrieval: 'embedding vector database'")
    hybrid_ret = HybridRetriever(store, dense, top_k=3, alpha=0.5)
    results = hybrid_ret.retrieve("embedding vector database")
    for r in results:
        print(f"      hybrid={r['score']:.4f} (vec={r['vec_score']:.3f}, bm25={r['bm25_score']:.3f}) | '{r['document'][:50]}...'")

    # ── PART 4: Full Query Engine ──
    print(f"\n{'─'*60}")
    print("📋 PART 4: Query Engine (Retrieve + Generate)")
    llm = LocalLLM("llama3.2")
    engine = RAGQueryEngine(hybrid_ret, llm)

    questions = [
        "Apa itu RAG dan bagaimana cara kerjanya?",
        "Apa saja contoh vector database?",
        "Bagaimana Ollama menjalankan LLM?",
    ]
    for q in questions:
        result = engine.query(q)

    print(f"\n{'='*70}")
    print("✅ RAG Pipeline: DIPELAJARI MENDALAM.")
    print("   Embedding (TF-IDF sparse + Dense semantic) ✓")
    print("   Vector Store (Chroma-style, cosine + hybrid) ✓")
    print("   Retriever (Dense + Hybrid with BM25) ✓")
    print("   Prompt Template (context injection) ✓")
    print("   LLM (Ollama-compatible, context-aware generation) ✓")
    print("   Query Engine (retrieve + generate + source attribution) ✓")
    print(f"{'='*70}")
