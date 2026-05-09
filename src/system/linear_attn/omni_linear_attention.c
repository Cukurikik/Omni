// @omni-layer System | @omni-lang C | @omni-batch 18 | @omni-semester 16
// @omni-repo AWEX + Fast-Transformer
// @omni-description Fast attention kernel: C implementation of linear
// attention with additive softmax approximation for O(n) complexity.

#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    float* data;
    int rows;
    int cols;
} OmniMatrix;

OmniMatrix omni_mat_alloc(int rows, int cols) {
    OmniMatrix m;
    m.rows = rows;
    m.cols = cols;
    m.data = (float*)calloc(rows * cols, sizeof(float));
    return m;
}

void omni_mat_free(OmniMatrix* m) {
    if (m->data) { free(m->data); m->data = NULL; }
}

// ELU+1 feature map for linear attention: phi(x) = elu(x) + 1
static inline float elu_plus_one(float x) {
    return x > 0.0f ? x + 1.0f : expf(x);
}

// Linear attention: O(n*d^2) instead of O(n^2*d)
void omni_linear_attention(
    const float* Q, const float* K, const float* V,
    float* output, int seq_len, int d_model, int n_heads
) {
    int head_dim = d_model / n_heads;
    for (int h = 0; h < n_heads; h++) {
        int offset = h * head_dim;
        // Compute S = sum_j phi(K_j)^T * V_j  [d_k x d_v]
        float* S = (float*)calloc(head_dim * head_dim, sizeof(float));
        float* z = (float*)calloc(head_dim, sizeof(float));
        for (int j = 0; j < seq_len; j++) {
            for (int a = 0; a < head_dim; a++) {
                float phi_k = elu_plus_one(K[j * d_model + offset + a]);
                z[a] += phi_k;
                for (int b = 0; b < head_dim; b++) {
                    S[a * head_dim + b] += phi_k * V[j * d_model + offset + b];
                }
            }
        }
        // output_i = phi(Q_i) * S / (phi(Q_i) * z)
        for (int i = 0; i < seq_len; i++) {
            float denom = 0.0f;
            for (int a = 0; a < head_dim; a++) {
                float phi_q = elu_plus_one(Q[i * d_model + offset + a]);
                denom += phi_q * z[a];
            }
            denom = fmaxf(denom, 1e-6f);
            for (int b = 0; b < head_dim; b++) {
                float num = 0.0f;
                for (int a = 0; a < head_dim; a++) {
                    float phi_q = elu_plus_one(Q[i * d_model + offset + a]);
                    num += phi_q * S[a * head_dim + b];
                }
                output[i * d_model + offset + b] = num / denom;
            }
        }
        free(S);
        free(z);
    }
}

// RoPE positional encoding
void omni_rope_encode(float* x, int seq_len, int d_model, float base) {
    for (int pos = 0; pos < seq_len; pos++) {
        for (int i = 0; i < d_model / 2; i++) {
            float freq = 1.0f / powf(base, 2.0f * i / d_model);
            float angle = pos * freq;
            float cos_a = cosf(angle), sin_a = sinf(angle);
            int idx0 = pos * d_model + 2 * i;
            int idx1 = idx0 + 1;
            float x0 = x[idx0], x1 = x[idx1];
            x[idx0] = x0 * cos_a - x1 * sin_a;
            x[idx1] = x0 * sin_a + x1 * cos_a;
        }
    }
}

// Layer normalization
void omni_layer_norm(float* x, int n, float eps) {
    float mean = 0.0f, var = 0.0f;
    for (int i = 0; i < n; i++) mean += x[i];
    mean /= n;
    for (int i = 0; i < n; i++) { float d = x[i] - mean; var += d * d; }
    var /= n;
    float inv = 1.0f / sqrtf(var + eps);
    for (int i = 0; i < n; i++) x[i] = (x[i] - mean) * inv;
}
