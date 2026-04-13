import os
import re
import math
import hashlib

# ==========================================
# 📄 OMNI RAG: Document Loader + Text Chunker (Phase 163)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# RAG dimulai dari DOKUMEN. Sebelum bisa di-embed atau di-search,
# dokumen harus melewati pipeline:
#
# 1. DOCUMENT LOADING — baca file dari berbagai format
#    - TXT: langsung baca
#    - Markdown: strip formatting tags
#    - PDF: extract text per halaman (PyMuPDF/pymupdf)
#    - DOCX: extract paragraphs (python-docx)
#    - Unstructured: handle format apapun
#
# 2. TEXT CHUNKING — potong dokumen jadi potongan kecil
#    KENAPA harus dipotong?
#    - LLM punya context window terbatas (4K-128K tokens)
#    - Embedding model punya batas input (512-8192 tokens)
#    - Chunk kecil → retrieval lebih presisi
#    - Chunk besar → konteks lebih lengkap
#
#    Strategi chunking:
#    a) Fixed-size: potong tiap N karakter (BODOH)
#    b) Recursive character splitter: coba potong di \n\n, lalu \n,
#       lalu '. ', lalu ' ' (LlamaIndex/LangChain default)
#    c) Semantic chunking: potong berdasarkan perubahan topik
#    d) Sentence-based: potong per kalimat
#
# 3. OVERLAP — setiap chunk HARUS overlap dengan chunk sebelumnya
#    Tanpa overlap, konteks di perbatasan chunk akan HILANG!
#    Contoh: overlap 200 char = 200 karakter terakhir chunk N
#    menjadi 200 karakter pertama chunk N+1.
#
# 4. METADATA — setiap chunk harus bawa metadata:
#    - source: file asal
#    - page: halaman (untuk PDF)
#    - chunk_index: urutan chunk
#    - total_chunks: jumlah total
#    Ini penting untuk ATTRIBUTION (menunjukkan sumber jawaban)

# ─────────────────────────────────────────────────
# KOMPONEN 1: Document Object
# ─────────────────────────────────────────────────
class Document:
    """
    Representasi satu dokumen yang sudah di-load.
    Mirip LlamaIndex Document object.
    """
    def __init__(self, text, metadata=None):
        self.text = text
        self.metadata = metadata or {}
        self.doc_id = hashlib.md5(text[:100].encode()).hexdigest()[:12]

    def __repr__(self):
        return f"Document(id={self.doc_id}, len={len(self.text)}, source={self.metadata.get('source', '?')})"


# ─────────────────────────────────────────────────
# KOMPONEN 2: Document Loaders
# ─────────────────────────────────────────────────
class TextLoader:
    """Load .txt files."""
    def load(self, text, source="unknown.txt"):
        return Document(text, {"source": source, "format": "txt"})


class MarkdownLoader:
    """Load .md files — strip formatting, preserve structure."""
    PATTERNS = [
        (r'^#{1,6}\s+', ''),       # Headers → plain text
        (r'\*\*(.+?)\*\*', r'\1'), # Bold
        (r'\*(.+?)\*', r'\1'),     # Italic
        (r'`(.+?)`', r'\1'),       # Inline code
        (r'!\[.*?\]\(.*?\)', ''),   # Images
        (r'\[(.+?)\]\(.*?\)', r'\1'), # Links → text only
    ]

    def load(self, text, source="unknown.md"):
        cleaned = text
        for pattern, replacement in self.PATTERNS:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)
        return Document(cleaned.strip(), {"source": source, "format": "markdown"})


class PDFLoader:
    """
    Simulasi PDF loader (dalam realita pakai PyMuPDF/pymupdf).
    PELAJARAN: PDF != teks. PDF adalah format VISUAL.
    Text extraction harus memahami layout, kolom, tabel.
    """
    def load(self, text, source="unknown.pdf", pages=None):
        # Simulasi multi-page PDF
        if pages is None:
            # Split by page markers
            page_texts = text.split("[PAGE_BREAK]") if "[PAGE_BREAK]" in text else [text]
        else:
            page_texts = pages

        documents = []
        for i, page_text in enumerate(page_texts):
            doc = Document(page_text.strip(), {
                "source": source,
                "format": "pdf",
                "page": i + 1,
                "total_pages": len(page_texts),
            })
            documents.append(doc)
        return documents


class DocxLoader:
    """
    Simulasi DOCX loader (dalam realita pakai python-docx).
    PELAJARAN: DOCX = ZIP berisi XML. Paragraphs = <w:p> elements.
    """
    def load(self, text, source="unknown.docx"):
        # Simulasi extract paragraphs
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        full_text = "\n".join(paragraphs)
        return Document(full_text, {"source": source, "format": "docx",
                                     "paragraphs": len(paragraphs)})


class SimpleDirectoryReader:
    """
    LlamaIndex-style directory reader — baca semua file di folder.
    Auto-detect format berdasarkan extension.
    """
    LOADERS = {
        ".txt": TextLoader(),
        ".md": MarkdownLoader(),
        ".pdf": PDFLoader(),
        ".docx": DocxLoader(),
    }

    def __init__(self, directory):
        self.directory = directory

    def load_data(self):
        """Load semua dokumen dari directory."""
        documents = []

        # Jika directory tidak ada, gunakan simulasi
        if not os.path.exists(self.directory):
            print(f"      ⚠️ Directory '{self.directory}' tidak ditemukan, menggunakan sample data")
            return self._load_sample_data()

        for filename in os.listdir(self.directory):
            filepath = os.path.join(self.directory, filename)
            if not os.path.isfile(filepath):
                continue

            ext = os.path.splitext(filename)[1].lower()
            loader = self.LOADERS.get(ext)
            if not loader:
                continue

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

            if ext == ".pdf":
                docs = loader.load(text, source=filename)
                documents.extend(docs if isinstance(docs, list) else [docs])
            else:
                doc = loader.load(text, source=filename)
                documents.append(doc)

        return documents

    def _load_sample_data(self):
        """Sample data untuk testing tanpa file fisik."""
        return [
            Document(
                "RAG adalah singkatan dari Retrieval-Augmented Generation. "
                "RAG bekerja dengan mencari dokumen yang relevan dari knowledge base, "
                "lalu menggunakan dokumen tersebut sebagai konteks untuk menjawab pertanyaan. "
                "Ini mengatasi masalah hallucination pada LLM karena jawaban berbasis fakta.",
                {"source": "rag_intro.txt", "format": "txt"}
            ),
            Document(
                "Vector database menyimpan embedding dalam bentuk vektor berdimensi tinggi. "
                "Pencarian dilakukan menggunakan similarity metric seperti cosine similarity "
                "atau dot product. Chroma, Qdrant, dan Weaviate adalah contoh vector database "
                "yang populer untuk aplikasi RAG.",
                {"source": "vectordb_guide.txt", "format": "txt"}
            ),
            Document(
                "LlamaIndex adalah framework RAG yang menghubungkan data source dengan LLM. "
                "Komponen utamanya: Document Loader untuk membaca data, "
                "Node Parser untuk chunking, Embedding untuk konversi ke vektor, "
                "Index untuk penyimpanan dan retrieval, dan Query Engine untuk tanya jawab.",
                {"source": "llamaindex_doc.txt", "format": "txt"}
            ),
            Document(
                "Ollama adalah platform untuk menjalankan LLM secara lokal. "
                "Ollama menggunakan llama.cpp sebagai backend inference. "
                "Modelfile di Ollama mirip Dockerfile — mendefinisikan FROM (base model), "
                "SYSTEM (persona), dan PARAMETER (temperature, top_k). "
                "API Ollama compatible dengan OpenAI format.",
                {"source": "ollama_guide.txt", "format": "txt"}
            ),
            Document(
                "Chunking strategy sangat mempengaruhi kualitas RAG. "
                "Recursive character splitter memotong teks pada separator natural: "
                "pertama coba paragraph break (dua newline), lalu newline tunggal, "
                "lalu titik+spasi, lalu spasi biasa. "
                "Overlap antar chunk mencegah kehilangan konteks di perbatasan.",
                {"source": "chunking_strategy.md", "format": "markdown"}
            ),
            Document(
                "Embedding model mengkonversi teks menjadi vektor berdimensi tinggi. "
                "Sentence-transformers dan nomic-embed-text adalah model embedding populer. "
                "Dimensi embedding biasanya 384, 768, atau 1536. "
                "Semakin tinggi dimensi, semakin kaya representasi semantik "
                "tapi semakin besar storage yang dibutuhkan.",
                {"source": "embedding_model.txt", "format": "txt"}
            ),
        ]


# ─────────────────────────────────────────────────
# KOMPONEN 3: Text Chunker (Recursive Character Splitter)
# ─────────────────────────────────────────────────
class RecursiveCharacterSplitter:
    """
    PELAJARAN KUNCI:
    Ini adalah DEFAULT splitter di LlamaIndex dan LangChain.

    Algoritma:
    1. Coba potong di separator pertama (\n\n = paragraph break)
    2. Jika hasilnya masih terlalu panjang, coba separator berikutnya (\n)
    3. Lalu '. ' (kalimat), lalu ' ' (kata), lalu per karakter
    4. Setiap chunk overlap dengan chunk sebelumnya

    Parameters:
    - chunk_size: target ukuran chunk (karakter)
    - chunk_overlap: jumlah karakter yang tumpang tindih
    - separators: urutan separator yang dicoba (paling natural duluan)
    """
    def __init__(self, chunk_size=500, chunk_overlap=100,
                 separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text):
        """Recursive splitting — core algorithm."""
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        # Coba setiap separator, dari yang paling natural
        for sep in self.separators:
            if sep == "":
                # Last resort: karakter per karakter
                chunks = [text[i:i + self.chunk_size]
                          for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
                return [c.strip() for c in chunks if c.strip()]

            parts = text.split(sep)
            if len(parts) <= 1:
                continue  # Separator tidak ditemukan, coba yang berikutnya

            # Gabungkan parts menjadi chunks yang sesuai ukuran
            chunks = []
            current_chunk = ""

            for part in parts:
                candidate = current_chunk + sep + part if current_chunk else part

                if len(candidate) <= self.chunk_size:
                    current_chunk = candidate
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # Jika part sendiri terlalu panjang, recurse
                    if len(part) > self.chunk_size:
                        sub_chunks = self._split_with_next_separator(part, sep)
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = part

            if current_chunk:
                chunks.append(current_chunk.strip())

            if chunks:
                # Apply overlap
                return self._apply_overlap(chunks)

        return [text.strip()] if text.strip() else []

    def _split_with_next_separator(self, text, current_sep):
        """Recurse ke separator berikutnya jika current tidak cukup."""
        idx = self.separators.index(current_sep) if current_sep in self.separators else 0
        sub_splitter = RecursiveCharacterSplitter(
            self.chunk_size, self.chunk_overlap,
            self.separators[idx + 1:] if idx + 1 < len(self.separators) else [""]
        )
        return sub_splitter.split_text(text)

    def _apply_overlap(self, chunks):
        """Tambahkan overlap antar chunks."""
        if self.chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks

        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            curr = chunks[i]
            # Ambil overlap dari akhir chunk sebelumnya
            overlap_text = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            combined = overlap_text + " " + curr
            overlapped.append(combined.strip())
        return overlapped

    def split_documents(self, documents):
        """Split list of Documents menjadi list of smaller Documents (nodes)."""
        nodes = []
        for doc in documents:
            chunks = self.split_text(doc.text)
            for i, chunk in enumerate(chunks):
                node = Document(chunk, {
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "parent_doc_id": doc.doc_id,
                })
                nodes.append(node)
        return nodes


# ─────────────────────────────────────────────────
# KOMPONEN 4: Sentence Splitter (Alternatif)
# ─────────────────────────────────────────────────
class SentenceSplitter:
    """
    Potong berdasarkan kalimat (sentence boundaries).
    Lebih natural daripada karakter, tapi lebih lambat.
    """
    SENTENCE_ENDINGS = re.compile(r'(?<=[.!?])\s+')

    def __init__(self, chunk_size=3, chunk_overlap=1):
        """chunk_size = jumlah kalimat per chunk."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        sentences = self.SENTENCE_ENDINGS.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        for i in range(0, len(sentences), self.chunk_size - self.chunk_overlap):
            chunk_sentences = sentences[i:i + self.chunk_size]
            if chunk_sentences:
                chunks.append(" ".join(chunk_sentences))
        return chunks


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("📄 OMNI RAG: Document Loader + Text Chunker")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Document Loading: TXT, Markdown (strip tags), PDF (pages), DOCX (paragraphs)")
    print("   Chunking: Recursive character splitter (LlamaIndex/LangChain default)")
    print("   Separators: \\n\\n → \\n → '. ' → ' ' → '' (paling natural duluan)")
    print("   Overlap: N karakter terakhir chunk jadi awal chunk berikutnya")
    print("   Metadata: source, page, chunk_index, parent_doc_id")

    # PART 1: Document Loaders
    print(f"\n{'─'*60}")
    print("📋 PART 1: Document Loaders")

    txt_loader = TextLoader()
    doc_txt = txt_loader.load("RAG adalah teknik AI yang powerful.", "readme.txt")
    print(f"   TXT: {doc_txt}")

    md_loader = MarkdownLoader()
    md_text = """# Heading
This is **bold** and *italic*.
Link: [click here](https://example.com)
`code` block."""
    doc_md = md_loader.load(md_text, "guide.md")
    print(f"   MD: {doc_md}")
    print(f"      Cleaned: '{doc_md.text[:60]}...'")

    pdf_loader = PDFLoader()
    pdf_text = "Halaman 1: Pendahuluan RAG.[PAGE_BREAK]Halaman 2: Implementasi.[PAGE_BREAK]Halaman 3: Evaluasi."
    docs_pdf = pdf_loader.load(pdf_text, "paper.pdf")
    print(f"   PDF: {len(docs_pdf)} pages extracted")
    for d in docs_pdf:
        print(f"      Page {d.metadata['page']}: '{d.text[:40]}'")

    docx_loader = DocxLoader()
    doc_docx = docx_loader.load("Paragraf 1.\nParagraf 2.\nParagraf 3.", "report.docx")
    print(f"   DOCX: {doc_docx} ({doc_docx.metadata['paragraphs']} paragraphs)")

    # PART 2: SimpleDirectoryReader (sample data)
    print(f"\n{'─'*60}")
    print("📋 PART 2: SimpleDirectoryReader")
    reader = SimpleDirectoryReader("./nonexistent_folder")
    documents = reader.load_data()
    print(f"   Loaded: {len(documents)} documents")
    for doc in documents:
        print(f"      {doc.metadata['source']}: {len(doc.text)} chars")

    # PART 3: Recursive Character Splitter
    print(f"\n{'─'*60}")
    print("📋 PART 3: Recursive Character Splitter")
    splitter = RecursiveCharacterSplitter(chunk_size=200, chunk_overlap=50)

    long_text = """RAG (Retrieval-Augmented Generation) adalah teknik yang menggabungkan pencarian informasi dengan generasi teks.

Pertama, sistem mencari dokumen yang relevan dari knowledge base menggunakan vector similarity search. Ini melibatkan encoding query menjadi embedding vektor.

Kedua, dokumen yang ditemukan dijadikan konteks tambahan untuk LLM. LLM kemudian menghasilkan jawaban berdasarkan konteks ini, bukan hanya dari pengetahuan internal.

Ketiga, hasilnya lebih akurat karena berbasis fakta dari dokumen. Ini mengurangi hallucination yang sering terjadi pada LLM biasa."""

    chunks = splitter.split_text(long_text)
    print(f"   Input: {len(long_text)} chars")
    print(f"   Output: {len(chunks)} chunks (size=200, overlap=50)")
    for i, chunk in enumerate(chunks):
        print(f"\n   Chunk {i+1} ({len(chunk)} chars):")
        print(f"   '{chunk[:80]}...'")

    # PART 4: Split Documents (full pipeline)
    print(f"\n{'─'*60}")
    print("📋 PART 4: Full Document → Node Pipeline")
    nodes = splitter.split_documents(documents)
    print(f"   Documents: {len(documents)} → Nodes: {len(nodes)}")
    for node in nodes[:5]:
        print(f"   📄 [{node.metadata['source']}] chunk {node.metadata['chunk_index']+1}/{node.metadata['total_chunks']}: '{node.text[:50]}...'")
    if len(nodes) > 5:
        print(f"   ... ({len(nodes)-5} more nodes)")

    # PART 5: Sentence Splitter (alternatif)
    print(f"\n{'─'*60}")
    print("📋 PART 5: Sentence Splitter (alternatif)")
    sent_splitter = SentenceSplitter(chunk_size=2, chunk_overlap=1)
    sent_chunks = sent_splitter.split_text("Kalimat pertama. Kalimat kedua. Kalimat ketiga. Kalimat keempat. Kalimat kelima.")
    print(f"   Input: 5 kalimat")
    print(f"   Output: {len(sent_chunks)} chunks (2 kalimat/chunk, overlap=1)")
    for i, c in enumerate(sent_chunks):
        print(f"   Chunk {i+1}: '{c}'")

    print(f"\n{'='*70}")
    print("✅ Document Loader + Chunker: DIPELAJARI MENDALAM.")
    print("   4 format loaders (TXT, MD, PDF, DOCX) ✓")
    print("   SimpleDirectoryReader (auto-detect format) ✓")
    print("   Recursive character splitter (5 separator levels) ✓")
    print("   Overlap mechanism ✓ | Sentence splitter ✓")
    print("   Metadata preservation (source, page, chunk_index) ✓")
    print(f"{'='*70}")
