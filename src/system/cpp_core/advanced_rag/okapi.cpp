#include <cstdint>

extern "C" {
    // OMNI System Layer - Okapi BM25 Term Calculation
    double compute_bm25_term(double idf, double tf, double doc_len, double avg_doc_len, double k1, double b) {
        if (avg_doc_len <= 0) return 0.0;
        double numerator = tf * (k1 + 1.0);
        double denominator = tf + k1 * (1.0 - b + b * (doc_len / avg_doc_len));
        return denominator == 0.0 ? 0.0 : idf * (numerator / denominator);
    }
}
