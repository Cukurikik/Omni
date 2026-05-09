/* @omni-layer System | @omni-source minimaxir/imgbeddings | @omni-lang C
 * @omni-description ONNX embedding kernel: optimized matrix-vector multiply
 * for CLIP visual projection with SIMD-ready inner product computation.
 */
#include <math.h>
#include <string.h>

typedef struct { float *data; int rows; int cols; } OmniMatrix;
typedef struct { float *data; int len; } OmniVector;
typedef struct { int ok; float result; const char *error; } OmniScalarResult;

static float omni_dot_product(const float *a, const float *b, int n) {
    float sum = 0.0f;
    int i = 0;
    /* Process 4 elements at a time for SIMD readiness */
    for (; i + 3 < n; i += 4) {
        sum += a[i]*b[i] + a[i+1]*b[i+1] + a[i+2]*b[i+2] + a[i+3]*b[i+3];
    }
    for (; i < n; i++) sum += a[i]*b[i];
    return sum;
}

void omni_matvec(const OmniMatrix *W, const OmniVector *x, OmniVector *out) {
    for (int r = 0; r < W->rows && r < out->len; r++) {
        out->data[r] = omni_dot_product(W->data + r * W->cols, x->data,
                                         W->cols < x->len ? W->cols : x->len);
    }
}

void omni_l2_normalize(float *vec, int n) {
    float norm = 0.0f;
    for (int i = 0; i < n; i++) norm += vec[i]*vec[i];
    norm = sqrtf(norm + 1e-8f);
    for (int i = 0; i < n; i++) vec[i] /= norm;
}

OmniScalarResult omni_cosine_similarity(const float *a, const float *b, int n) {
    OmniScalarResult r = {1, 0.0f, NULL};
    float dot = 0.0f, na = 0.0f, nb = 0.0f;
    for (int i = 0; i < n; i++) {
        dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i];
    }
    na = sqrtf(na + 1e-8f); nb = sqrtf(nb + 1e-8f);
    r.result = dot / (na * nb);
    return r;
}

void omni_relu_inplace(float *data, int n) {
    for (int i = 0; i < n; i++) {
        if (data[i] < 0.0f) data[i] = 0.0f;
    }
}

void omni_gelu_inplace(float *data, int n) {
    for (int i = 0; i < n; i++) {
        float x = data[i];
        data[i] = 0.5f * x * (1.0f + tanhf(0.7978845608f * (x + 0.044715f * x*x*x)));
    }
}
