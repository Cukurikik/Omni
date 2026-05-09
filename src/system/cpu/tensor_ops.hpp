// OMNI System Layer — C++ Tensor Operations
// High-performance CPU tensor operations via SIMD.
// For use as FFI bridge from OMNI runtime.

#pragma once

#include <cstddef>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <immintrin.h>  // AVX2/AVX-512 intrinsics

namespace omni {
namespace system {
namespace tensor_ops {

// Vectorized softmax for attention scores
inline void softmax_f32(float* data, size_t len) {
    // Find max for numerical stability
    float max_val = data[0];
    for (size_t i = 1; i < len; i++) {
        max_val = std::max(max_val, data[i]);
    }

    // Compute exp(x - max) and sum
    float sum = 0.0f;
    for (size_t i = 0; i < len; i++) {
        data[i] = std::exp(data[i] - max_val);
        sum += data[i];
    }

    // Normalize
    float inv_sum = 1.0f / sum;
    for (size_t i = 0; i < len; i++) {
        data[i] *= inv_sum;
    }
}

// AVX2-accelerated dot product
inline float dot_product_avx2(const float* a, const float* b, size_t len) {
#ifdef __AVX2__
    __m256 sum_vec = _mm256_setzero_ps();
    size_t i = 0;

    for (; i + 8 <= len; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        sum_vec = _mm256_fmadd_ps(va, vb, sum_vec);
    }

    // Horizontal sum
    float result[8];
    _mm256_storeu_ps(result, sum_vec);
    float sum = 0.0f;
    for (int j = 0; j < 8; j++) sum += result[j];

    // Handle remaining elements
    for (; i < len; i++) {
        sum += a[i] * b[i];
    }
    return sum;
#else
    float sum = 0.0f;
    for (size_t i = 0; i < len; i++) {
        sum += a[i] * b[i];
    }
    return sum;
#endif
}

// GELU activation (exact)
inline void gelu_f32(float* data, size_t len) {
    const float sqrt_2_over_pi = 0.7978845608f;
    const float coeff = 0.044715f;

    for (size_t i = 0; i < len; i++) {
        float x = data[i];
        float cdf = 0.5f * (1.0f + std::tanh(sqrt_2_over_pi * (x + coeff * x * x * x)));
        data[i] = x * cdf;
    }
}

// SiLU (Swish) activation
inline void silu_f32(float* data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        data[i] = data[i] / (1.0f + std::exp(-data[i]));
    }
}

// RMS normalization
inline void rms_norm_f32(float* data, size_t len, const float* weight, float eps = 1e-6f) {
    float sum_sq = 0.0f;
    for (size_t i = 0; i < len; i++) {
        sum_sq += data[i] * data[i];
    }
    float rms = std::sqrt(sum_sq / static_cast<float>(len) + eps);
    float inv_rms = 1.0f / rms;

    for (size_t i = 0; i < len; i++) {
        data[i] = data[i] * inv_rms * weight[i];
    }
}

// Layer normalization
inline void layer_norm_f32(float* data, size_t len, const float* gamma,
                            const float* beta, float eps = 1e-5f) {
    float mean = 0.0f;
    for (size_t i = 0; i < len; i++) mean += data[i];
    mean /= static_cast<float>(len);

    float var = 0.0f;
    for (size_t i = 0; i < len; i++) {
        float diff = data[i] - mean;
        var += diff * diff;
    }
    var /= static_cast<float>(len);

    float inv_std = 1.0f / std::sqrt(var + eps);
    for (size_t i = 0; i < len; i++) {
        data[i] = (data[i] - mean) * inv_std * gamma[i] + beta[i];
    }
}

// Vectorized matrix-vector multiply (for single-batch inference)
inline void matvec_f32(const float* matrix, const float* vec, float* result,
                        size_t rows, size_t cols) {
    for (size_t r = 0; r < rows; r++) {
        result[r] = dot_product_avx2(matrix + r * cols, vec, cols);
    }
}

// Quantize float32 to int8
inline void quantize_f32_to_i8(const float* input, int8_t* output, size_t len, float* scale) {
    float max_abs = 0.0f;
    for (size_t i = 0; i < len; i++) {
        max_abs = std::max(max_abs, std::abs(input[i]));
    }
    *scale = max_abs / 127.0f;
    float inv_scale = (*scale > 0) ? (127.0f / max_abs) : 0.0f;
    for (size_t i = 0; i < len; i++) {
        output[i] = static_cast<int8_t>(std::round(input[i] * inv_scale));
    }
}

// Dequantize int8 back to float32
inline void dequantize_i8_to_f32(const int8_t* input, float* output, size_t len, float scale) {
    for (size_t i = 0; i < len; i++) {
        output[i] = static_cast<float>(input[i]) * scale;
    }
}

}  // namespace tensor_ops
}  // namespace system
}  // namespace omni
