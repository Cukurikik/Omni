#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - L2 Norm for Gradient Compressors
    double compute_l2_norm(const double* vector, int32_t len) {
        if (!vector || len <= 0) return 0.0;
        double sum_sq = 0.0;
        for(int32_t i=0; i<len; i++) {
            sum_sq += vector[i] * vector[i];
        }
        return std::sqrt(sum_sq);
    }
}
