#include <cstdint>
#include <cmath>

// OMNI System Kernel: Cosine similarity for collaborative filtering
extern "C" {
        double compute(const double* vec_a, const double* vec_b, int32_t len) {
            double dot = 0.0, norm_a = 0.0, norm_b = 0.0;
            for(int i=0; i<len; i++) {
                dot += vec_a[i] * vec_b[i];
                norm_a += vec_a[i] * vec_a[i];
                norm_b += vec_b[i] * vec_b[i];
            }
            return (norm_a > 0 && norm_b > 0) ? (dot / (std::sqrt(norm_a) * std::sqrt(norm_b))) : 0.0;
        }
}