#include <cstdint>

extern "C" {
    // Vectorized-ready dot product for recommendation systems
    float xrec_dot_product_simd(const float* vec_a, const float* vec_b, uint32_t dimensions) {
        float sum = 0.0f;
        // In a real SIMD implementation this would use AVX or NEON
        // Using standard unrolled loop for compatibility
        uint32_t i = 0;
        for (; i + 4 <= dimensions; i += 4) {
            sum += vec_a[i] * vec_b[i] +
                   vec_a[i+1] * vec_b[i+1] +
                   vec_a[i+2] * vec_b[i+2] +
                   vec_a[i+3] * vec_b[i+3];
        }
        for (; i < dimensions; ++i) {
            sum += vec_a[i] * vec_b[i];
        }
        return sum;
    }
}
