/* @omni-layer System | @omni-source jakobhoeg/browser-ai | @omni-lang C
 * @omni-description WASM tensor ops: optimized matrix operations for
 * browser-based transformer inference with float16 support.
 */
#include <math.h>
#include <stdint.h>
#include <string.h>

#define OMNI_TILE_SIZE 16

typedef uint16_t float16_t;  /* IEEE 754 half precision stub */

static float f16_to_f32(float16_t h) {
    uint32_t sign = (h >> 15) & 1;
    uint32_t exp  = (h >> 10) & 0x1F;
    uint32_t frac = h & 0x3FF;
    if (exp == 0) return sign ? -0.0f : 0.0f;
    if (exp == 31) return sign ? -INFINITY : INFINITY;
    float result = ldexpf((float)(1024 + frac), (int)exp - 25);
    return sign ? -result : result;
}

static float16_t f32_to_f16(float f) {
    uint32_t bits;
    memcpy(&bits, &f, 4);
    uint16_t sign = (bits >> 16) & 0x8000;
    int32_t exp = ((bits >> 23) & 0xFF) - 127 + 15;
    uint16_t frac = (bits >> 13) & 0x3FF;
    if (exp <= 0) return sign;
    if (exp >= 31) return sign | 0x7C00;
    return sign | ((uint16_t)exp << 10) | frac;
}

void omni_gemm_f32(const float *A, const float *B, float *C, int M, int N, int K) {
    memset(C, 0, sizeof(float) * M * N);
    for (int i = 0; i < M; i++) {
        for (int k = 0; k < K; k++) {
            float a_ik = A[i * K + k];
            for (int j = 0; j < N; j++) {
                C[i * N + j] += a_ik * B[k * N + j];
            }
        }
    }
}

void omni_softmax_f32(float *data, int n) {
    float max_val = data[0];
    for (int i = 1; i < n; i++) if (data[i] > max_val) max_val = data[i];
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        data[i] = expf(data[i] - max_val);
        sum += data[i];
    }
    for (int i = 0; i < n; i++) data[i] /= (sum + 1e-8f);
}

void omni_layer_norm_f32(float *data, int n, float eps) {
    float mean = 0.0f, var = 0.0f;
    for (int i = 0; i < n; i++) mean += data[i];
    mean /= n;
    for (int i = 0; i < n; i++) {
        float d = data[i] - mean;
        var += d * d;
    }
    var /= n;
    float inv_std = 1.0f / sqrtf(var + eps);
    for (int i = 0; i < n; i++) {
        data[i] = (data[i] - mean) * inv_std;
    }
}

void omni_residual_add(float *out, const float *a, const float *b, int n) {
    for (int i = 0; i < n; i++) out[i] = a[i] + b[i];
}
