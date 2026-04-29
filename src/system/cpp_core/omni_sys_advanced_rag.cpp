#include <cstdint>
#include <cmath>

// OMNI System Kernel: Okapi BM25 Ranking
extern "C" {
        double compute(const double* tfs, int32_t len, double doc_len, double avg_doc_len) {
            double k1 = 1.5, b = 0.75, score = 0.0;
            for(int i=0; i<len; i++) {
                double tf = tfs[i];
                score += (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len)));
            }
            return score;
        }
}