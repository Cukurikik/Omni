// OMNI System — C++ SIMD Quantized MatMul
// INT8/INT4 quantized matrix multiplication with AVX2.
#include <cstdint>
#include <cstring>
#include <algorithm>
#ifdef __AVX2__
#include <immintrin.h>
#endif

namespace omni {
namespace quant {

struct QuantBlock {
    int8_t data[32];
    float scale;
    float zero_point;
};

void quantize_f32_to_i8(const float* input, int8_t* output, float* scale, float* zero, int n) {
    float min_val = *std::min_element(input, input + n);
    float max_val = *std::max_element(input, input + n);
    *scale = (max_val - min_val) / 255.0f;
    *zero = -min_val / *scale;
    float inv_scale = 1.0f / *scale;
    for (int i = 0; i < n; i++) {
        int v = (int)(input[i] * inv_scale + *zero + 0.5f);
        output[i] = (int8_t)std::max(0, std::min(255, v)) - 128;
    }
}

void dequantize_i8_to_f32(const int8_t* input, float* output, float scale, float zero, int n) {
    for (int i = 0; i < n; i++) {
        output[i] = ((float)(input[i] + 128) - zero) * scale;
    }
}

#ifdef __AVX2__
void matmul_i8_avx2(const int8_t* A, const int8_t* B, int32_t* C, int M, int K, int N) {
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            __m256i sum = _mm256_setzero_si256();
            int k = 0;
            for (; k + 31 < K; k += 32) {
                __m256i va = _mm256_loadu_si256((__m256i*)&A[i * K + k]);
                __m256i vb = _mm256_loadu_si256((__m256i*)&B[j * K + k]);
                __m256i lo_a = _mm256_cvtepi8_epi16(_mm256_castsi256_si128(va));
                __m256i lo_b = _mm256_cvtepi8_epi16(_mm256_castsi256_si128(vb));
                sum = _mm256_add_epi32(sum, _mm256_madd_epi16(lo_a, lo_b));
            }
            int32_t result[8]; _mm256_storeu_si256((__m256i*)result, sum);
            int32_t s = 0;
            for (int r = 0; r < 8; r++) s += result[r];
            for (; k < K; k++) s += (int32_t)A[i*K+k] * (int32_t)B[j*K+k];
            C[i * N + j] = s;
        }
    }
}
#else
void matmul_i8_avx2(const int8_t* A, const int8_t* B, int32_t* C, int M, int K, int N) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            int32_t s = 0;
            for (int k = 0; k < K; k++) s += (int32_t)A[i*K+k] * (int32_t)B[j*K+k];
            C[i*N+j] = s;
        }
}
#endif

float compute_quantization_error(const float* original, const float* reconstructed, int n) {
    float mse = 0.0f;
    for (int i = 0; i < n; i++) {
        float d = original[i] - reconstructed[i];
        mse += d * d;
    }
    return mse / (float)n;
}

} // namespace quant
} // namespace omni
