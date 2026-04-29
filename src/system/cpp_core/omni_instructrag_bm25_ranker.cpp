// Omni InstructRAG Document Ranker (C++)
// System Layer: High-perf BM25 scoring for RAG retrieval.
// Ref: weizhepei/InstructRAG — ICLR 2025
#include <cmath>
#include <cstring>
#include <cstddef>
double omni_bm25_score(int tf, int df, int doc_len, double avg_dl, int n_docs, double k1, double b) {
    if (df <= 0 || n_docs <= 0 || avg_dl <= 0) return 0.0;
    double idf = log((n_docs - df + 0.5) / (df + 0.5) + 1.0);
    double tf_norm = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (doc_len / avg_dl)));
    return idf * tf_norm;
}
