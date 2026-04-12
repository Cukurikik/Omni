import math
import time
import json
from collections import defaultdict

# ==========================================
# 📊 OMNI RAG ENGINE: Evaluation & Monitoring (Phase 139)
# ==========================================
# Mempelajari 4 RAG Evaluation tools:
#   36. RAGAS    → Faithfulness, Answer Relevancy, Context Precision/Recall (DIPELAJARI)
#   37. TruLens  → Dashboard monitoring + feedback functions (DIPELAJARI)
#   38. DeepEval → pytest-style LLM testing (DIPELAJARI)
#   39. Langfuse → Observability, trace, cost tracking (DIPELAJARI)

class OmniRAGEvaluator:
    """
    Merangkum semua metrik evaluasi RAG:
    - RAGAS metrics (faithfulness, relevancy, precision, recall)
    - TruLens feedback functions
    - DeepEval test cases
    - Langfuse trace logging
    """

    def __init__(self):
        self.traces = []
        self.test_results = []
        print("📊 [OMNI-EVAL] RAG Evaluator diinisiasi (RAGAS + TruLens + DeepEval + Langfuse).")

    # ── RAGAS Metrics ──────────────────────────────
    def faithfulness(self, answer: str, context: str) -> float:
        """RAGAS Faithfulness: Apakah jawaban didukung oleh konteks?"""
        answer_tokens = set(answer.lower().split())
        context_tokens = set(context.lower().split())
        if not answer_tokens:
            return 0.0
        overlap = answer_tokens & context_tokens
        return round(len(overlap) / len(answer_tokens), 4)

    def answer_relevancy(self, question: str, answer: str) -> float:
        """RAGAS Answer Relevancy: Apakah jawaban relevan dengan pertanyaan?"""
        q_tokens = set(question.lower().split())
        a_tokens = set(answer.lower().split())
        if not q_tokens:
            return 0.0
        overlap = q_tokens & a_tokens
        return round(len(overlap) / len(q_tokens), 4)

    def context_precision(self, question: str, contexts: list) -> float:
        """RAGAS Context Precision: Apakah chunk yang ditemukan presisi?"""
        q_tokens = set(question.lower().split())
        relevant = 0
        for ctx in contexts:
            ctx_tokens = set(ctx.lower().split())
            if len(q_tokens & ctx_tokens) > 0:
                relevant += 1
        return round(relevant / max(len(contexts), 1), 4)

    def context_recall(self, answer: str, contexts: list) -> float:
        """RAGAS Context Recall: Apakah semua informasi di jawaban tercakup konteks?"""
        a_tokens = set(answer.lower().split())
        covered = set()
        for ctx in contexts:
            covered |= (a_tokens & set(ctx.lower().split()))
        return round(len(covered) / max(len(a_tokens), 1), 4)

    # ── TruLens Feedback Functions ──────────────────
    def trulens_groundedness(self, answer: str, sources: list) -> float:
        """TruLens Groundedness: Seberapa 'grounded' jawaban pada sumber?"""
        return self.faithfulness(answer, " ".join(sources))

    # ── DeepEval Test Cases ──────────────────────────
    def deepeval_test(self, test_name: str, question: str, answer: str,
                      context: str, expected_min_score: float = 0.5) -> dict:
        """DeepEval pytest-style test case."""
        faith = self.faithfulness(answer, context)
        relevancy = self.answer_relevancy(question, answer)
        avg_score = (faith + relevancy) / 2

        passed = avg_score >= expected_min_score
        result = {
            "test_name": test_name,
            "faithfulness": faith,
            "relevancy": relevancy,
            "avg_score": round(avg_score, 4),
            "passed": passed,
            "threshold": expected_min_score
        }
        self.test_results.append(result)
        return result

    # ── Langfuse Trace Logging ──────────────────────
    def langfuse_trace(self, trace_id: str, step: str, input_data: str,
                       output_data: str, latency_ms: float, cost_usd: float = 0.0):
        """Langfuse observability trace."""
        trace = {
            "trace_id": trace_id,
            "step": step,
            "input": input_data[:50],
            "output": output_data[:50],
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "timestamp": time.time()
        }
        self.traces.append(trace)
        return trace

    # ── Full Evaluation Report ─────────────────────
    def evaluate_full(self, question: str, answer: str, contexts: list) -> dict:
        """Jalankan semua metrik evaluasi sekaligus."""
        context_combined = " ".join(contexts)

        metrics = {
            "faithfulness": self.faithfulness(answer, context_combined),
            "answer_relevancy": self.answer_relevancy(question, answer),
            "context_precision": self.context_precision(question, contexts),
            "context_recall": self.context_recall(answer, contexts),
            "groundedness": self.trulens_groundedness(answer, contexts),
        }

        # Log ke Langfuse
        self.langfuse_trace("eval_001", "evaluation", question, json.dumps(metrics), 15.0)

        return metrics

    def print_dashboard(self):
        """TruLens-style dashboard output."""
        print("\n┌────────────────────────────────────────────────────────┐")
        print("│           📊 OMNI RAG EVALUATION DASHBOARD            │")
        print("├────────────────────────────────────────────────────────┤")

        if self.test_results:
            print("│  DeepEval Test Results:                                │")
            for t in self.test_results:
                status = "✅ PASS" if t["passed"] else "❌ FAIL"
                print(f"│    {status} {t['test_name']:<20} score={t['avg_score']:.3f}  │")

        if self.traces:
            print("│  Langfuse Traces:                                      │")
            total_cost = sum(t["cost_usd"] for t in self.traces)
            total_latency = sum(t["latency_ms"] for t in self.traces)
            print(f"│    Traces: {len(self.traces)} | Cost: ${total_cost:.4f} | Latency: {total_latency:.1f}ms │")

        print("└────────────────────────────────────────────────────────┘")


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("📊 OMNI RAG EVALUATOR — MENGUASAI RAGAS + TruLens + DeepEval + Langfuse")
    print("=" * 70)

    evaluator = OmniRAGEvaluator()

    question = "Apa itu OMNI Framework dan bahasa apa yang didukung?"
    answer = "OMNI Framework adalah sistem polylingual yang mendukung Rust, Go, Python, dan C++ untuk membangun aplikasi enterprise."
    contexts = [
        "OMNI Framework adalah sistem polylingual yang menyatukan 15 bahasa pemrograman.",
        "Rust digunakan untuk keamanan memori. Go untuk concurrency. C++ untuk performa.",
        "LLVM compiler mengkompilasi semua bahasa ke satu binary.",
    ]

    # Full evaluation
    print("\n🔬 [EVAL] Menjalankan evaluasi lengkap...")
    metrics = evaluator.evaluate_full(question, answer, contexts)
    for name, score in metrics.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"   {name:<22} {bar} {score:.4f}")

    # DeepEval tests
    print("\n🧪 [DEEPEVAL] Menjalankan test suite...")
    evaluator.deepeval_test("test_omni_qa", question, answer, " ".join(contexts), 0.3)
    evaluator.deepeval_test("test_irrelevant", "Berapa harga beras?", answer, " ".join(contexts), 0.5)

    # Langfuse traces
    evaluator.langfuse_trace("trace_001", "retrieval", question, "3 chunks found", 12.5, 0.0015)
    evaluator.langfuse_trace("trace_001", "generation", "context...", answer[:50], 245.0, 0.0120)

    evaluator.print_dashboard()

    print("\n" + "=" * 70)
    print("✅ OMNI RAG EVALUATOR: 4 platform evaluasi dalam SATU engine.")
    print("   RAGAS (metrics) ✓ | TruLens (groundedness) ✓")
    print("   DeepEval (pytest) ✓ | Langfuse (traces) ✓")
    print("=" * 70)
