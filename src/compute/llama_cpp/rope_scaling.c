#include <math.h>

// OMNI llama.cpp: Rotary Position Embeddings (RoPE)
// Applies RoPE to Q and K tensors to inject positional information, supporting context scaling.
// Source: ggerganov/llama.cpp

typedef enum {
    ROPE_SUCCESS = 0,
    ROPE_ERR_NULL = 1
} rope_err_t;

// Applies standard RoPE to a 1D tensor representing a single head
rope_err_t llama_apply_rope_forward(float* q, float* k, int n_dims, int pos, float base) {
    if (!q || !k) return ROPE_ERR_NULL;

    for (int i = 0; i < n_dims; i += 2) {
        float theta = (float)pos * powf(base, -(float)i / n_dims);
        float cos_theta = cosf(theta);
        float sin_theta = sinf(theta);

        // Apply to Q
        float q0 = q[i];
        float q1 = q[i+1];
        q[i]   = q0 * cos_theta - q1 * sin_theta;
        q[i+1] = q0 * sin_theta + q1 * cos_theta;

        // Apply to K
        float k0 = k[i];
        float k1 = k[i+1];
        k[i]   = k0 * cos_theta - k1 * sin_theta;
        k[i+1] = k0 * sin_theta + k1 * cos_theta;
    }

    return ROPE_SUCCESS;
}

// Applies Linear Scaling RoPE for context extension (e.g. extending 4k to 8k)
rope_err_t llama_apply_rope_linear_scaled(float* q, float* k, int n_dims, int pos, float base, float scale) {
    if (!q || !k) return ROPE_ERR_NULL;

    // Scale the position
    float scaled_pos = (float)pos / scale;

    for (int i = 0; i < n_dims; i += 2) {
        float theta = scaled_pos * powf(base, -(float)i / n_dims);
        float cos_theta = cosf(theta);
        float sin_theta = sinf(theta);

        float q0 = q[i];
        float q1 = q[i+1];
        q[i]   = q0 * cos_theta - q1 * sin_theta;
        q[i+1] = q0 * sin_theta + q1 * cos_theta;

        float k0 = k[i];
        float k1 = k[i+1];
        k[i]   = k0 * cos_theta - k1 * sin_theta;
        k[i+1] = k0 * sin_theta + k1 * cos_theta;
    }

    return ROPE_SUCCESS;
}
