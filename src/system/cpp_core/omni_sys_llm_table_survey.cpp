#include <cstdint>
#include <cmath>

// OMNI System Kernel: TF-IDF term frequency calculation
extern "C" {
        double compute(const double* term_freqs, const double* doc_freqs, int32_t len, double total_docs) {
            double sum = 0.0;
            for(int i=0; i<len; i++) {
                double idf = std::log(total_docs / (1.0 + doc_freqs[i]));
                sum += term_freqs[i] * idf;
            }
            return sum;
        }
}