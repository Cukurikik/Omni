// moe_fast_gelu.cpp — Compute / Low-Level
// Layer: Compute / C++ — MoE Activation Functions
//
// Optimized Fast GELU implementation for MoE Feed-Forward Networks.
// Approximates the GELU activation using tanh, heavily vectorized using AVX2.

#include <immintrin.h>
#include <cmath>

namespace omni {
namespace moe {

// Constants for Fast GELU: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
const float SQRT_2_OVER_PI = 0.7978845608f;
const float COEF_CUBIC = 0.044715f;

/**
 * Standard scalar Fast GELU
 */
inline float fast_gelu_scalar(float x) {
    float x_cube = x * x * x;
    float inner = SQRT_2_OVER_PI * (x + COEF_CUBIC * x_cube);
    return 0.5f * x * (1.0f + std::tanh(inner));
}

/**
 * Applies Fast GELU in-place over an array using AVX2.
 * Used internally within MoE expert layers to maximize throughput.
 */
void apply_fast_gelu_avx2(float* data, size_t size) {
    size_t i = 0;

    // Load constants
    __m256 v_half = _mm256_set1_ps(0.5f);
    __m256 v_one = _mm256_set1_ps(1.0f);
    __m256 v_sqrt_2_pi = _mm256_set1_ps(SQRT_2_OVER_PI);
    __m256 v_coef = _mm256_set1_ps(COEF_CUBIC);

    for (; i + 7 < size; i += 8) {
        __m256 vx = _mm256_loadu_ps(&data[i]);

        // x^3
        __m256 vx2 = _mm256_mul_ps(vx, vx);
        __m256 vx3 = _mm256_mul_ps(vx2, vx);

        // 0.044715 * x^3
        __m256 v_inner1 = _mm256_mul_ps(v_coef, vx3);

        // x + 0.044715 * x^3
        __m256 v_inner2 = _mm256_add_ps(vx, v_inner1);

        // sqrt(2/pi) * (...)
        __m256 v_inner3 = _mm256_mul_ps(v_sqrt_2_pi, v_inner2);

        // Compute tanh approximation.
        // A full precise AVX tanh is complex. For maximum speed, we use an approximation
        // or a library call like SVML if available. Here we fallback to scalar for exact match,
        // but normally we'd inline an approximation (e.g. rational polynomial).
        // For demonstration, we unroll into scalar tanh temporarily.
        
        alignas(32) float tmp[8];
        _mm256_store_ps(tmp, v_inner3);
        for(int j=0; j<8; j++) {
            tmp[j] = std::tanh(tmp[j]);
        }
        __m256 v_tanh = _mm256_load_ps(tmp);

        // 1 + tanh
        __m256 v_1_plus_tanh = _mm256_add_ps(v_one, v_tanh);

        // 0.5 * x * (1 + tanh)
        __m256 v_half_x = _mm256_mul_ps(v_half, vx);
        __m256 v_out = _mm256_mul_ps(v_half_x, v_1_plus_tanh);

        _mm256_storeu_ps(&data[i], v_out);
    }

    // Scalar fallback for remainder
    for (; i < size; ++i) {
        data[i] = fast_gelu_scalar(data[i]);
    }
}

} // namespace moe
} // namespace omni
