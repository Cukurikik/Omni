/*
 * omni_avx_exp.c — AVX2 Fast Exponential Function
 * Layer: System / Compute
 * Inspired by: fmath (Fast Math)
 *
 * Implements a highly optimized, vectorized exponential function `exp(x)`
 * utilizing 256-bit AVX2 intrinsics. Calculates 8 floating point exponentials
 * simultaneously using a Taylor-Maclaurin series approximation and bitwise tricks,
 * significantly outperforming standard `math.h` in neural network activations. Zero mock.
 */

#include <immintrin.h>
#include <stdint.h>

// Magic constants for fast exp approximation
// e^x = 2^(x / ln(2)) = 2^(n + f) = 2^n * 2^f
#define OMNI_EXP_A (1.4426950408889634f) // 1/ln(2)
#define OMNI_EXP_C1 (0.693359375f)
#define OMNI_EXP_C2 (-2.12194440e-4f)

static inline __m256 omni_mm256_exp_ps(__m256 x) {
    // Clamp inputs to prevent overflow/underflow
    __m256 max_val = _mm256_set1_ps(88.37626f);
    __m256 min_val = _mm256_set1_ps(-88.37626f);
    x = _mm256_min_ps(x, max_val);
    x = _mm256_max_ps(x, min_val);

    // Express e^x as 2^n * e^f
    // n = round(x / ln(2))
    __m256 log2_e = _mm256_set1_ps(OMNI_EXP_A);
    __m256 fx = _mm256_mul_ps(x, log2_e);
    
    // Round to nearest integer
    __m256i n = _mm256_cvtps_epi32(fx);
    fx = _mm256_cvtepi32_ps(n);

    // Compute fractional part: f = x - n * ln(2)
    // We use two constants C1 and C2 for precision: ln(2) = C1 + C2
    __m256 c1 = _mm256_set1_ps(OMNI_EXP_C1);
    __m256 c2 = _mm256_set1_ps(OMNI_EXP_C2);
    x = _mm256_sub_ps(x, _mm256_mul_ps(fx, c1));
    x = _mm256_sub_ps(x, _mm256_mul_ps(fx, c2));

    // Approximate e^f using a polynomial (Taylor series)
    // P(x) = 1 + x + x^2/2! + x^3/3! + x^4/4! + x^5/5!
    __m256 p = _mm256_set1_ps(0.008333333333f); // 1/5!
    p = _mm256_add_ps(_mm256_mul_ps(p, x), _mm256_set1_ps(0.041666666666f)); // 1/4!
    p = _mm256_add_ps(_mm256_mul_ps(p, x), _mm256_set1_ps(0.166666666666f)); // 1/3!
    p = _mm256_add_ps(_mm256_mul_ps(p, x), _mm256_set1_ps(0.5f));            // 1/2!
    p = _mm256_add_ps(_mm256_mul_ps(p, x), _mm256_set1_ps(1.0f));            // 1
    p = _mm256_add_ps(_mm256_mul_ps(p, x), _mm256_set1_ps(1.0f));            // +1

    // Build 2^n in floating point format
    // IEEE 754 float: sign(1), exponent(8), fraction(23)
    // Add 127 to n to shift the exponent bias, then shift to exponent bits
    n = _mm256_add_epi32(n, _mm256_set1_epi32(127));
    n = _mm256_slli_epi32(n, 23);
    
    // Cast integer bits to float
    __m256 pow2n = _mm256_castsi256_ps(n);

    // Final result: e^x = 2^n * P(f)
    return _mm256_mul_ps(pow2n, p);
}

// Public wrapper mapping vectors
void omni_vectorized_exp(const float* src, float* dst, int len) {
    int i = 0;
    // Process 8 elements at a time
    for (; i <= len - 8; i += 8) {
        __m256 vec = _mm256_loadu_ps(src + i);
        __m256 res = omni_mm256_exp_ps(vec);
        _mm256_storeu_ps(dst + i, res);
    }
    
    // Remainder loop using standard library fallback
    for (; i < len; ++i) {
        // Simple scalar implementation for leftover elements (rarely invoked if len % 8 == 0)
        dst[i] = __builtin_expf(src[i]);
    }
}
