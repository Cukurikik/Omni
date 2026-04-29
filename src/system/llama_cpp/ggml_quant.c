#include <stdint.h>
#include <stddef.h>
#include <math.h>

// OMNI llama.cpp: GGML Vector Quantization
// Core logic for quantizing float32 arrays into 8-bit integers (Q8_0 format).
// Source: ggerganov/llama.cpp

#define QK8_0 32

typedef struct {
    float   d;          // delta (scaling factor)
    int8_t  qs[QK8_0];  // quantized values
} block_q8_0;

typedef enum {
    GGML_SUCCESS = 0,
    GGML_ERR_NULL_PTR = 1,
    GGML_ERR_INVALID_SIZE = 2
} ggml_error_t;

// Quantize an array of floats into Q8_0 blocks
// n must be a multiple of QK8_0 (32)
ggml_error_t ggml_quantize_q8_0(const float * x, void * vy, int n) {
    if (!x || !vy) return GGML_ERR_NULL_PTR;
    if (n % QK8_0 != 0) return GGML_ERR_INVALID_SIZE;

    block_q8_0 * y = (block_q8_0 *) vy;
    const int num_blocks = n / QK8_0;

    for (int i = 0; i < num_blocks; i++) {
        float amax = 0.0f; // absolute max

        // Find the absolute maximum in the block
        for (int j = 0; j < QK8_0; j++) {
            float v = x[i*QK8_0 + j];
            float abs_v = fabsf(v);
            if (abs_v > amax) {
                amax = abs_v;
            }
        }

        // Calculate scaling factor (delta)
        // 127 is the maximum positive value of an 8-bit signed integer
        const float d = amax / 127.0f;
        const float id = (d != 0.0f) ? 1.0f / d : 0.0f;

        y[i].d = d;

        // Quantize
        for (int j = 0; j < QK8_0; j++) {
            float v = x[i*QK8_0 + j] * id;
            // Round to nearest integer
            y[i].qs[j] = (int8_t)roundf(v);
        }
    }

    return GGML_SUCCESS;
}

// Dequantize Q8_0 blocks back to float32
ggml_error_t ggml_dequantize_q8_0(const void * vx, float * y, int n) {
    if (!vx || !y) return GGML_ERR_NULL_PTR;
    if (n % QK8_0 != 0) return GGML_ERR_INVALID_SIZE;

    const block_q8_0 * x = (const block_q8_0 *) vx;
    const int num_blocks = n / QK8_0;

    for (int i = 0; i < num_blocks; i++) {
        const float d = x[i].d;

        for (int j = 0; j < QK8_0; j++) {
            y[i*QK8_0 + j] = x[i].qs[j] * d;
        }
    }

    return GGML_SUCCESS;
}
