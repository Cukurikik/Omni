// omni_simd_attention.c — SIMD-Accelerated Attention Kernel
// Inspired by: SoundStorm/RQ-Transformer compute requirements
// Layer: System / C Kernel
//
// AVX2/NEON vectorized dot-product attention for production inference.
// Zero-dependency C kernel for embedding into OMNI runtime.

#include <stdint.h>
#include <stddef.h>
#include <math.h>
#include <float.h>
#include <string.h>
#include <stdlib.h>

#ifdef __AVX2__
#include <immintrin.h>
#endif

#ifdef __ARM_NEON
#include <arm_neon.h>
#endif

// ============================================================================
// Data structures
// ============================================================================

typedef struct {
    float* data;
    int32_t rows;
    int32_t cols;
    int32_t stride;  // row stride in floats
} OmniMatrix;

typedef struct {
    float temperature;
    int32_t use_causal_mask;
    int32_t num_heads;
    int32_t head_dim;
} AttentionParams;

// ============================================================================
// SIMD dot-product kernels
// ============================================================================

static float dot_product_scalar(const float* a, const float* b, int32_t n) {
    float sum = 0.0f;
    for (int32_t i = 0; i < n; i++) {
        sum += a[i] * b[i];
    }
    return sum;
}

#ifdef __AVX2__
static float dot_product_avx2(const float* a, const float* b, int32_t n) {
    __m256 acc = _mm256_setzero_ps();
    int32_t i = 0;

    for (; i + 8 <= n; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        acc = _mm256_fmadd_ps(va, vb, acc);
    }

    // Horizontal sum
    __m128 hi = _mm256_extractf128_ps(acc, 1);
    __m128 lo = _mm256_castps256_ps128(acc);
    __m128 sum4 = _mm_add_ps(lo, hi);
    __m128 sum2 = _mm_add_ps(sum4, _mm_movehl_ps(sum4, sum4));
    __m128 sum1 = _mm_add_ss(sum2, _mm_shuffle_ps(sum2, sum2, 1));
    float result = _mm_cvtss_f32(sum1);

    // Handle remainder
    for (; i < n; i++) {
        result += a[i] * b[i];
    }
    return result;
}
#endif

#ifdef __ARM_NEON
static float dot_product_neon(const float* a, const float* b, int32_t n) {
    float32x4_t acc = vdupq_n_f32(0.0f);
    int32_t i = 0;

    for (; i + 4 <= n; i += 4) {
        float32x4_t va = vld1q_f32(a + i);
        float32x4_t vb = vld1q_f32(b + i);
        acc = vfmaq_f32(acc, va, vb);
    }

    float result = vaddvq_f32(acc);
    for (; i < n; i++) {
        result += a[i] * b[i];
    }
    return result;
}
#endif

static float dot_product(const float* a, const float* b, int32_t n) {
#ifdef __AVX2__
    return dot_product_avx2(a, b, n);
#elif defined(__ARM_NEON)
    return dot_product_neon(a, b, n);
#else
    return dot_product_scalar(a, b, n);
#endif
}

// ============================================================================
// Softmax (numerically stable)
// ============================================================================

static void softmax_inplace(float* scores, int32_t n) {
    float max_val = -FLT_MAX;
    for (int32_t i = 0; i < n; i++) {
        if (scores[i] > max_val) max_val = scores[i];
    }

    float sum = 0.0f;
    for (int32_t i = 0; i < n; i++) {
        scores[i] = expf(scores[i] - max_val);
        sum += scores[i];
    }

    float inv_sum = 1.0f / (sum + 1e-10f);
    for (int32_t i = 0; i < n; i++) {
        scores[i] *= inv_sum;
    }
}

// ============================================================================
// Scaled dot-product attention for a single head
// ============================================================================

// Computes: output = softmax(Q * K^T / sqrt(d)) * V
// Q: (seq_q, head_dim)
// K: (seq_kv, head_dim)
// V: (seq_kv, head_dim)
// output: (seq_q, head_dim)
int32_t omni_scaled_dot_attention(
    const float* Q, int32_t seq_q,
    const float* K, int32_t seq_kv,
    const float* V,
    float* output,
    int32_t head_dim,
    float scale,
    int32_t use_causal_mask
) {
    if (!Q || !K || !V || !output) return -1;
    if (seq_q <= 0 || seq_kv <= 0 || head_dim <= 0) return -2;

    float* attn_scores = (float*)malloc((size_t)seq_kv * sizeof(float));
    if (!attn_scores) return -3;

    for (int32_t q = 0; q < seq_q; q++) {
        const float* q_vec = Q + q * head_dim;

        // Compute attention scores
        for (int32_t k = 0; k < seq_kv; k++) {
            if (use_causal_mask && k > q) {
                attn_scores[k] = -1e9f;
            } else {
                attn_scores[k] = dot_product(q_vec, K + k * head_dim, head_dim) * scale;
            }
        }

        softmax_inplace(attn_scores, seq_kv);

        // Weighted sum of values
        float* out_vec = output + q * head_dim;
        memset(out_vec, 0, (size_t)head_dim * sizeof(float));

        for (int32_t v = 0; v < seq_kv; v++) {
            float w = attn_scores[v];
            if (w < 1e-10f) continue;
            const float* v_vec = V + v * head_dim;
            for (int32_t d = 0; d < head_dim; d++) {
                out_vec[d] += w * v_vec[d];
            }
        }
    }

    free(attn_scores);
    return 0;
}

// ============================================================================
// Multi-head attention
// ============================================================================

int32_t omni_multi_head_attention(
    const float* Q,         // (batch * seq_q, num_heads * head_dim)
    const float* K,         // (batch * seq_kv, num_heads * head_dim)
    const float* V,
    float* output,
    int32_t batch_size,
    int32_t seq_q,
    int32_t seq_kv,
    const AttentionParams* params
) {
    if (!Q || !K || !V || !output || !params) return -1;

    int32_t num_heads = params->num_heads;
    int32_t head_dim = params->head_dim;
    float scale = 1.0f / sqrtf((float)head_dim);
    if (params->temperature > 0.0f) {
        scale /= params->temperature;
    }

    int32_t full_dim = num_heads * head_dim;

    for (int32_t b = 0; b < batch_size; b++) {
        for (int32_t h = 0; h < num_heads; h++) {
            // Extract head-specific Q, K, V slices
            // In practice these would be pre-split; here we compute offsets
            int32_t batch_offset_q = b * seq_q * full_dim;
            int32_t batch_offset_kv = b * seq_kv * full_dim;
            int32_t batch_offset_out = b * seq_q * full_dim;

            // Allocate per-head buffers
            float* q_head = (float*)malloc((size_t)seq_q * head_dim * sizeof(float));
            float* k_head = (float*)malloc((size_t)seq_kv * head_dim * sizeof(float));
            float* v_head = (float*)malloc((size_t)seq_kv * head_dim * sizeof(float));
            float* o_head = (float*)malloc((size_t)seq_q * head_dim * sizeof(float));

            if (!q_head || !k_head || !v_head || !o_head) {
                free(q_head); free(k_head); free(v_head); free(o_head);
                return -3;
            }

            // Gather head slices
            for (int32_t s = 0; s < seq_q; s++) {
                memcpy(q_head + s * head_dim,
                       Q + batch_offset_q + s * full_dim + h * head_dim,
                       (size_t)head_dim * sizeof(float));
            }
            for (int32_t s = 0; s < seq_kv; s++) {
                memcpy(k_head + s * head_dim,
                       K + batch_offset_kv + s * full_dim + h * head_dim,
                       (size_t)head_dim * sizeof(float));
                memcpy(v_head + s * head_dim,
                       V + batch_offset_kv + s * full_dim + h * head_dim,
                       (size_t)head_dim * sizeof(float));
            }

            int32_t ret = omni_scaled_dot_attention(
                q_head, seq_q, k_head, seq_kv, v_head, o_head,
                head_dim, scale, params->use_causal_mask
            );

            if (ret != 0) {
                free(q_head); free(k_head); free(v_head); free(o_head);
                return ret;
            }

            // Scatter results back
            for (int32_t s = 0; s < seq_q; s++) {
                memcpy(output + batch_offset_out + s * full_dim + h * head_dim,
                       o_head + s * head_dim,
                       (size_t)head_dim * sizeof(float));
            }

            free(q_head);
            free(k_head);
            free(v_head);
            free(o_head);
        }
    }

    return 0;
}
