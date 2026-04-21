ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI QUIVR ENGINE — RAG Knowledge Base & Semantic Search
# ===========================================================================
# Source Paradigm: https://github.com/QuivrHQ/quivr
# Domain Layer  : Compute (RAG / Knowledge Management)
# Zero-Mock     : 100% Native — os, json, re, hashlib, sqlite3, math
# ===========================================================================
"""
Quivr teaches us:
  1. Document ingestion (text, markdown, structured data)
  2. Chunking strategies (fixed-size, sentence, paragraph)
  3. TF-IDF based search without external ML libraries
  4. Knowledge base organization (brains/collections)
  5. Chat-style Q&A over documents
  6. Source attribution and citation tracking

This engine distills those paradigms into OMNI-native Python for
document RAG with TF-IDF search, chunking, and knowledge management.
"""

import hashlib
import json
import math
import os
import re
import sqlite3
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    source: str = ""
    doc_type: str = "text"   # text, markdown, json
    chunks: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class SearchResult:
    chunk: str
    score: float
    doc_id: str
    doc_title: str
    chunk_index: int


@dataclass
class Brain:
    brain_id: str
    name: str
    description: str = ""
    doc_count: int = 0
    chunk_count: int = 0


# ── Text Chunker ──────────────────────────────────────────────────────────

class TextChunker:
    """Split documents into searchable chunks."""

    @staticmethod
    def chunk_by_sentences(text: str, max_sentences: int = 5) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        for i in range(0, len(sentences), max_sentences):
            chunk = " ".join(sentences[i:i + max_sentences]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    @staticmethod
    def chunk_by_paragraphs(text: str) -> List[str]:
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 20]

    @staticmethod
    def chunk_by_size(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap
        return chunks

    @staticmethod
    def chunk_markdown(text: str) -> List[str]:
        sections = re.split(r'\n#{1,3}\s+', text)
        return [s.strip() for s in sections if s.strip() and len(s.strip()) > 20]


# ── TF-IDF Search Engine ─────────────────────────────────────────────────

class TFIDFEngine:
    """Pure-Python TF-IDF search engine — no external dependencies."""

    STOP_WORDS = frozenset([
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "can", "could", "and", "or", "but", "if",
        "then", "else", "when", "at", "by", "for", "with", "about", "between",
        "through", "to", "from", "in", "on", "of", "that", "this", "it", "its",
        "not", "no", "nor", "as", "so", "than", "too", "very", "just",
    ])

    @staticmethod
    def tokenize(text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        return [w for w in words if w not in TFIDFEngine.STOP_WORDS and len(w) > 1]

    @staticmethod
    def tf(tokens: List[str]) -> Dict[str, float]:
        counts = Counter(tokens)
        total = len(tokens) or 1
        return {w: c / total for w, c in counts.items()}

    @staticmethod
    def build_idf(corpus: List[List[str]]) -> Dict[str, float]:
        N = len(corpus) or 1
        df = Counter()
        for doc_tokens in corpus:
            for word in set(doc_tokens):
                df[word] += 1
        return {w: math.log(N / (1 + count)) for w, count in df.items()}

    @staticmethod
    def tfidf_vector(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
        tf = TFIDFEngine.tf(tokens)
        return {w: tf_val * idf.get(w, 0) for w, tf_val in tf.items()}

    @staticmethod
    def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0
        dot = sum(vec_a[k] * vec_b[k] for k in common_keys)
        mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
        mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


# ── Knowledge Store (SQLite) ─────────────────────────────────────────────

class KnowledgeStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".quivr_brain.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".quivr_brain.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY, title TEXT,
                source TEXT, content_length INTEGER,
                chunk_count INTEGER, ingested_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY, doc_id TEXT,
                chunk_index INTEGER, content TEXT,
                tokens TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT, top_result TEXT, score REAL, queried_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save_document(self, doc: Document, chunk_tokens: List[List[str]]):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)",
                      (doc.doc_id, doc.title, doc.source,
                       len(doc.content), len(doc.chunks), time.time()))
        for i, (chunk, tokens) in enumerate(zip(doc.chunks, chunk_tokens)):
            cid = hashlib.sha256(f"{doc.doc_id}_{i}".encode()).hexdigest()[:12]
            conn.execute("INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?)",
                          (cid, doc.doc_id, i, chunk[:2000],
                           json.dumps(tokens[:200])))
        conn.commit()
        conn.close()

    def get_all_chunks(self) -> List[Tuple[str, str, int, str, List[str]]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""SELECT c.chunk_id, c.doc_id, c.chunk_index, c.content, c.tokens,
                     d.title FROM chunks c JOIN documents d ON c.doc_id = d.doc_id""")
        results = []
        for row in c.fetchall():
            tokens = json.loads(row[4]) if row[4] else []
            results.append((row[0], row[1], row[2], row[3], tokens, row[5]))
        conn.close()
        return results

    def log_query(self, query: str, top_result: str, score: float):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO queries (query,top_result,score,queried_at) VALUES (?,?,?,?)",
                      (query[:200], top_result[:200], score, time.time()))
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM documents")
        docs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM chunks")
        chunks = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM queries")
        queries = c.fetchone()[0]
        conn.close()
        return {"documents": docs, "chunks": chunks, "queries": queries}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniQuivrEngine:
    """
    OMNI Quivr Engine — Zero-Mock RAG Knowledge Base & Semantic Search.

    Capabilities (all native stdlib):
      - Document ingestion with multiple chunking strategies
      - TF-IDF based semantic search (pure Python, no ML deps)
      - Cosine similarity scoring
      - Knowledge base management (SQLite)
      - Query logging and analytics
      - Multi-format support (text, markdown)
    """

    def __init__(self):
        self.chunker = TextChunker()
        self.tfidf = TFIDFEngine()
        self.store = KnowledgeStore()

    def ingest(self, title: str, content: str, source: str = "",
                chunk_method: str = "sentences") -> Dict:
        doc_id = hashlib.sha256(f"{title}{time.time()}".encode()).hexdigest()[:12]

        if chunk_method == "paragraphs":
            chunks = self.chunker.chunk_by_paragraphs(content)
        elif chunk_method == "fixed":
            chunks = self.chunker.chunk_by_size(content)
        elif chunk_method == "markdown":
            chunks = self.chunker.chunk_markdown(content)
        else:
            chunks = self.chunker.chunk_by_sentences(content)

        if not chunks:
            chunks = [content[:1000]]

        doc = Document(doc_id=doc_id, title=title, content=content,
                        source=source, chunks=chunks)
        chunk_tokens = [self.tfidf.tokenize(c) for c in chunks]
        self.store.save_document(doc, chunk_tokens)

        return {"doc_id": doc_id, "title": title, "chunks": len(chunks),
                "total_tokens": sum(len(t) for t in chunk_tokens)}

    def search(self, query: str, top_k: int = 5) -> Dict:
        query_tokens = self.tfidf.tokenize(query)
        all_chunks = self.store.get_all_chunks()

        if not all_chunks:
            return {"query": query, "results": [], "message": "No documents ingested"}

        # Build IDF from all chunks
        corpus = [row[4] for row in all_chunks]  # tokens
        idf = self.tfidf.build_idf(corpus)

        # Score each chunk
        query_vec = self.tfidf.tfidf_vector(query_tokens, idf)
        scored = []
        for chunk_id, doc_id, idx, content, tokens, doc_title in all_chunks:
            chunk_vec = self.tfidf.tfidf_vector(tokens, idf)
            score = self.tfidf.cosine_similarity(query_vec, chunk_vec)
            if score > 0.01:
                scored.append({
                    "chunk": content[:300], "score": round(score, 4),
                    "doc_title": doc_title, "chunk_index": idx,
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[:top_k]

        if top:
            self.store.log_query(query, top[0]["chunk"][:100], top[0]["score"])

        return {"query": query, "results": top, "total_matches": len(scored)}

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniQuivrEngine",
            "status": "active",
            "db": self.store.stats(),
            "chunk_methods": ["sentences", "paragraphs", "fixed", "markdown"],
            "capabilities": ["doc_ingest", "multi_chunk", "tfidf_search",
                             "cosine_similarity", "query_log", "knowledge_base",
                             "source_attribution"],
        }


if __name__ == "__main__":
    engine = OmniQuivrEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
