// OMNI System — C++ High-Performance Transformer Block
// Optimized with SIMD intrinsics for CPU inference.
#include <cmath>
#include <cstring>
#include <vector>
#include <algorithm>
#include <immintrin.h>

namespace omni {

void rmsnorm(float* out, const float* x, const float* weight, int n, float eps = 1e-5f) {
    float ss = 0.0f;
    for (int i = 0; i < n; i++) ss += x[i] * x[i];
    ss = 1.0f / sqrtf(ss / (float)n + eps);
    for (int i = 0; i < n; i++) out[i] = weight[i] * (x[i] * ss);
}

void softmax(float* x, int n) {
    float max_val = *std::max_element(x, x + n);
    float sum = 0.0f;
    for (int i = 0; i < n; i++) { x[i] = expf(x[i] - max_val); sum += x[i]; }
    float inv = 1.0f / sum;
    for (int i = 0; i < n; i++) x[i] *= inv;
}

#ifdef __AVX2__
void matmul_avx2(float* out, const float* a, const float* b, int M, int K, int N) {
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            __m256 sum = _mm256_setzero_ps();
            int k = 0;
            for (; k + 7 < K; k += 8) {
                __m256 va = _mm256_loadu_ps(&a[i * K + k]);
                __m256 vb = _mm256_loadu_ps(&b[j * K + k]); // B transposed
                sum = _mm256_fmadd_ps(va, vb, sum);
            }
            float result[8]; _mm256_storeu_ps(result, sum);
            float s = result[0]+result[1]+result[2]+result[3]+result[4]+result[5]+result[6]+result[7];
            for (; k < K; k++) s += a[i * K + k] * b[j * K + k];
            out[i * N + j] = s;
        }
    }
}
#else
void matmul_avx2(float* out, const float* a, const float* b, int M, int K, int N) {
    for (int i = 0; i < M; i++)
        for (int j = 0; j < N; j++) {
            float s = 0; for (int k = 0; k < K; k++) s += a[i*K+k]*b[j*K+k];
            out[i*N+j] = s;
        }
}
#endif

void silu(float* x, int n) { for (int i = 0; i < n; i++) x[i] = x[i] / (1.0f + expf(-x[i])); }
void gelu(float* x, int n) {
    for (int i = 0; i < n; i++) {
        float v = x[i];
        x[i] = 0.5f * v * (1.0f + tanhf(0.7978845608f * (v + 0.044715f * v * v * v)));
    }
}

struct TransformerConfig {
    int dim; int hidden_dim; int num_heads; int head_dim;
    int vocab_size; int max_seq_len; int num_layers;
};

struct AttentionState {
    std::vector<float> key_cache;   // [layers, seq, heads, head_dim]
    std::vector<float> value_cache;
    int cached_len = 0;
};

void attention_forward(float* output, const float* q, AttentionState& state,
                       int layer, int pos, const TransformerConfig& cfg) {
    int h = cfg.num_heads, d = cfg.head_dim;
    std::vector<float> scores(pos + 1);

    for (int head = 0; head < h; head++) {
        const float* qi = q + head * d;
        for (int t = 0; t <= pos; t++) {
            float s = 0.0f;
            const float* ki = state.key_cache.data() + (layer * cfg.max_seq_len * h * d) + t * h * d + head * d;
            for (int i = 0; i < d; i++) s += qi[i] * ki[i];
            scores[t] = s / sqrtf((float)d);
        }
        softmax(scores.data(), pos + 1);
        float* oi = output + head * d;
        std::memset(oi, 0, d * sizeof(float));
        for (int t = 0; t <= pos; t++) {
            const float* vi = state.value_cache.data() + (layer * cfg.max_seq_len * h * d) + t * h * d + head * d;
            for (int i = 0; i < d; i++) oi[i] += scores[t] * vi[i];
        }
    }
}

} // namespace omni
