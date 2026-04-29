#include <cstdint>

extern "C" {
    // OMNI System Layer - Mistral Vector Dot Product
    double compute_dot_product(const double* a, const double* b, int32_t len) {
        if (!a || !b || len <= 0) return 0.0;
        double dot = 0.0;
        for(int32_t i = 0; i < len; ++i) {
            dot += a[i] * b[i];
        }
        return dot;
    }
}
