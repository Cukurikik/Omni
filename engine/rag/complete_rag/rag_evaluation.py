import math
import re
import sys
from collections import Counter

# ==========================================
# 📊 OMNI RAG: Evaluation Engine (Phase 166)
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# RAG tanpa evaluasi = BUTA. Kita HARUS bisa mengukur kualitas RAG.
#
# 3 dimensi evaluasi RAG (RAG Triad):
#
# 1. CONTEXT RELEVANCE — apakah retriever mengambil chunk yang TEPAT?
#    Metrik: Precision@K, Recall@K, MRR (Mean Reciprocal Rank)
#    Jika chunk yang diambil tidak relevan → jawaban pasti buruk!
#
# 2. ANSWER FAITHFULNESS — apakah jawaban KONSISTEN dengan konteks?
#    Metrik: Overlap ratio antara jawaban dan konteks
#    Jika LLM "mengkhayal" diluar konteks → hallucination!
#
# 3. ANSWER RELEVANCE — apakah jawaban MENJAWAB pertanyaan?
#    Metrik: Keyword overlap query—answer
#    Jika jawaban baik tapi tidak nyambung → gagal!
#
# TOOLS EVALUASI PRODUCTION:
#   - RAGAS (ragas.io): Otomatis evaluasi RAG dengan LLM-as-judge
#   - TruLens: Tracing + evaluation framework
#   - DeepEval: Unit testing framework khusus RAG

# ─────────────────────────────────────────────────
# METRIC 1: Context Relevance
# ─────────────────────────────────────────────────
class ContextRelevanceEvaluator:
    """
    Mengukur apakah chunks yang di-retrieve RELEVAN dengan query.
    Precision@K = berapa persen dari K chunks yang relevan.
    """
    def __init__(self):
        self.results = []

    def _keyword_overlap(self, text_a, text_b):
        """Hitung keyword overlap sebagai proxy relevansi."""
        words_a = set(re.findall(r'\b\w{3,}\b', text_a.lower()))
        words_b = set(re.findall(r'\b\w{3,}\b', text_b.lower()))
        if not words_a or not words_b:
            return 0.0
        overlap = len(words_a & words_b)
        return overlap / len(words_a)

    def evaluate(self, query, retrieved_chunks, relevance_threshold=0.15):
        relevant_count = 0
        chunk_scores = []

        for chunk in retrieved_chunks:
            score = self._keyword_overlap(query, chunk)
            is_relevant = score >= relevance_threshold
            if is_relevant:
                relevant_count += 1
            chunk_scores.append({"chunk": chunk[:50], "score": score, "relevant": is_relevant})

        precision = relevant_count / len(retrieved_chunks) if retrieved_chunks else 0
        result = {
            "metric": "Context Relevance (Precision@K)",
            "query": query,
            "k": len(retrieved_chunks),
            "relevant": relevant_count,
            "precision": precision,
            "chunks": chunk_scores,
        }
        self.results.append(result)
        return result


# ─────────────────────────────────────────────────
# METRIC 2: Answer Faithfulness
# ─────────────────────────────────────────────────
class FaithfulnessEvaluator:
    """
    Mengukur apakah jawaban SETIA pada konteks (tidak hallucinate).
    Setiap klaim di jawaban harus bisa dilacak ke context.
    """
    def evaluate(self, answer, context):
        answer_words = set(re.findall(r'\b\w{3,}\b', answer.lower()))
        context_words = set(re.findall(r'\b\w{3,}\b', context.lower()))

        if not answer_words:
            return {"metric": "Faithfulness", "score": 0, "grounded_ratio": 0}

        grounded = answer_words & context_words
        ratio = len(grounded) / len(answer_words)

        return {
            "metric": "Answer Faithfulness",
            "total_answer_words": len(answer_words),
            "grounded_in_context": len(grounded),
            "hallucinated": len(answer_words - context_words),
            "faithfulness_score": round(ratio, 4),
            "verdict": "FAITHFUL" if ratio >= 0.6 else "HALLUCINATION_RISK",
        }


# ─────────────────────────────────────────────────
# METRIC 3: Answer Relevance
# ─────────────────────────────────────────────────
class AnswerRelevanceEvaluator:
    """
    Mengukur apakah jawaban MENJAWAB pertanyaan yang diajukan.
    """
    def evaluate(self, query, answer):
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        answer_words = set(re.findall(r'\b\w{3,}\b', answer.lower()))

        if not query_words:
            return {"metric": "Answer Relevance", "score": 0}

        overlap = query_words & answer_words
        coverage = len(overlap) / len(query_words)

        return {
            "metric": "Answer Relevance",
            "query_terms": len(query_words),
            "covered_in_answer": len(overlap),
            "relevance_score": round(coverage, 4),
            "verdict": "RELEVANT" if coverage >= 0.3 else "OFF_TOPIC",
        }


# ─────────────────────────────────────────────────
# METRIC 4: BLEU Score (Machine Translation metric, berguna untuk RAG)
# ─────────────────────────────────────────────────
class BLEUEvaluator:
    """
    BLEU = Bilingual Evaluation Understudy.
    Mengukur overlap n-gram antara jawaban dan referensi.
    """
    def _ngrams(self, tokens, n):
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

    def evaluate(self, reference, candidate, max_n=4):
        ref_tokens = re.findall(r'\b\w+\b', reference.lower())
        cand_tokens = re.findall(r'\b\w+\b', candidate.lower())

        if not cand_tokens or not ref_tokens:
            return {"metric": "BLEU", "score": 0}

        precisions = []
        for n in range(1, max_n + 1):
            ref_ngrams = Counter(self._ngrams(ref_tokens, n))
            cand_ngrams = Counter(self._ngrams(cand_tokens, n))

            clipped = sum(min(count, ref_ngrams.get(ng, 0)) for ng, count in cand_ngrams.items())
            total = sum(cand_ngrams.values())

            if total == 0:
                precisions.append(0)
            else:
                precisions.append(clipped / total)

        # Geometric mean of precisions
        if any(p == 0 for p in precisions):
            bleu = 0
        else:
            log_avg = sum(math.log(p) for p in precisions) / len(precisions)
            bleu = math.exp(log_avg)

        # Brevity penalty
        bp = min(1.0, math.exp(1 - len(ref_tokens) / max(len(cand_tokens), 1)))
        bleu *= bp

        return {
            "metric": "BLEU",
            "precisions": [round(p, 4) for p in precisions],
            "brevity_penalty": round(bp, 4),
            "bleu_score": round(bleu, 4),
        }


# ─────────────────────────────────────────────────
# METRIC 5: RAG Triad (Full Evaluation)
# ─────────────────────────────────────────────────
class RAGTriadEvaluator:
    """
    PELAJARAN: RAG Triad = evaluasi HOLISTIC.
    Mengukur 3 dimensi sekaligus:
    1. Context Relevance (retrieval quality)
    2. Faithfulness (grounding quality)
    3. Answer Relevance (response quality)
    """
    def __init__(self):
        self.context_eval = ContextRelevanceEvaluator()
        self.faithful_eval = FaithfulnessEvaluator()
        self.relevance_eval = AnswerRelevanceEvaluator()
        self.bleu_eval = BLEUEvaluator()

    def evaluate(self, query, retrieved_chunks, answer, reference_answer=None):
        context_text = " ".join(retrieved_chunks)

        ctx = self.context_eval.evaluate(query, retrieved_chunks)
        faith = self.faithful_eval.evaluate(answer, context_text)
        rel = self.relevance_eval.evaluate(query, answer)

        bleu = None
        if reference_answer:
            bleu = self.bleu_eval.evaluate(reference_answer, answer)

        # Overall score (weighted average)
        overall = (ctx["precision"] * 0.3 + faith["faithfulness_score"] * 0.4 + rel["relevance_score"] * 0.3)

        return {
            "query": query,
            "context_relevance": ctx["precision"],
            "faithfulness": faith["faithfulness_score"],
            "answer_relevance": rel["relevance_score"],
            "bleu": bleu["bleu_score"] if bleu else None,
            "overall_score": round(overall, 4),
            "grade": "A" if overall >= 0.7 else "B" if overall >= 0.5 else "C" if overall >= 0.3 else "F",
        }


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("📊 OMNI RAG: Evaluation Engine — RAG Triad + BLEU")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   RAG Triad: Context Relevance + Faithfulness + Answer Relevance")
    print("   BLEU: n-gram precision + brevity penalty")
    print("   Tools: RAGAS, TruLens, DeepEval (yang saya replika arsitekturnya)")

    # Test cases
    test_cases = [
        {
            "query": "Apa itu RAG dan bagaimana cara kerjanya?",
            "chunks": [
                "RAG adalah singkatan dari Retrieval-Augmented Generation. RAG bekerja dengan mencari dokumen relevan.",
                "Vector database menyimpan embedding untuk pencarian similarity.",
                "Python adalah bahasa pemrograman serbaguna.",
            ],
            "answer": "RAG (Retrieval-Augmented Generation) bekerja dengan mencari dokumen relevan dari knowledge base menggunakan vector database, lalu dokumen tersebut digunakan sebagai konteks untuk LLM.",
            "reference": "RAG singkatan Retrieval-Augmented Generation, bekerja dengan retrieval dokumen relevan lalu augment ke LLM.",
        },
        {
            "query": "Bagaimana Ollama menjalankan LLM secara lokal?",
            "chunks": [
                "Ollama adalah platform menjalankan LLM lokal menggunakan llama.cpp sebagai backend inference.",
                "Ollama API compatible dengan OpenAI format di localhost:11434.",
                "React framework untuk frontend web.",
            ],
            "answer": "Ollama menjalankan LLM secara lokal menggunakan llama.cpp sebagai backend inference engine. API-nya compatible dengan OpenAI format.",
            "reference": "Ollama menjalankan LLM lokal via llama.cpp, expose API di localhost:11434.",
        },
        {
            "query": "Cara membuat embedding?",
            "chunks": [
                "Kucing suka makan ikan.",
                "Burung bisa terbang tinggi.",
                "Anjing adalah sahabat manusia.",
            ],
            "answer": "Embedding dibuat menggunakan model neural network yang mengkonversi teks ke vektor berdimensi tinggi.",
            "reference": "Embedding model mengkonversi teks menjadi vektor, bisa pakai sentence-transformers atau nomic-embed-text.",
        },
    ]

    triad = RAGTriadEvaluator()

    print(f"\n{'─'*60}")
    print("📋 RAG TRIAD EVALUATION")

    all_scores = []
    for i, tc in enumerate(test_cases):
        print(f"\n   Case {i+1}: \"{tc['query']}\"")
        result = triad.evaluate(tc["query"], tc["chunks"], tc["answer"], tc["reference"])

        print(f"      Context Relevance: {result['context_relevance']:.2f}")
        print(f"      Faithfulness:      {result['faithfulness']:.4f}")
        print(f"      Answer Relevance:  {result['answer_relevance']:.4f}")
        if result['bleu'] is not None:
            print(f"      BLEU Score:        {result['bleu']:.4f}")
        print(f"      Overall: {result['overall_score']:.4f} (Grade: {result['grade']})")
        all_scores.append(result)

    # Summary
    avg_overall = sum(r["overall_score"] for r in all_scores) / len(all_scores)
    print(f"\n{'─'*60}")
    print(f"📊 SUMMARY REPORT")
    print(f"   Cases evaluated: {len(all_scores)}")
    print(f"   Average overall: {avg_overall:.4f}")
    print(f"   Grades: {', '.join(r['grade'] for r in all_scores)}")
    print(f"\n   Analysis:")
    for r in all_scores:
        issues = []
        if r["context_relevance"] < 0.5:
            issues.append("retrieval tidak tepat")
        if r["faithfulness"] < 0.5:
            issues.append("risiko hallucination")
        if r["answer_relevance"] < 0.3:
            issues.append("jawaban off-topic")
        if issues:
            print(f"      ⚠️ \"{r['query'][:30]}...\" → {', '.join(issues)}")
        else:
            print(f"      ✅ \"{r['query'][:30]}...\" → semua dimensi baik")

    print(f"\n{'='*70}")
    print("✅ RAG Evaluation: DIPELAJARI MENDALAM.")
    print("   Context Relevance (Precision@K) ✓")
    print("   Answer Faithfulness (grounding check) ✓")
    print("   Answer Relevance (query coverage) ✓")
    print("   BLEU Score (n-gram precision + brevity penalty) ✓")
    print("   RAG Triad (holistic evaluation + grading) ✓")
    print(f"{'='*70}")
