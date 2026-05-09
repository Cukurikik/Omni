// @omni-layer System | @omni-lang C | @omni-batch 18 | @omni-semester 16
// @omni-description C SIMD-optimized quantization kernels: int8/int4
// quantize/dequantize for transformer weight compression.

#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct {
    float scale;
    float zero_point;
    int bits;
} QuantParams;

// Compute quantization parameters for a float array
QuantParams compute_quant_params(const float* data, int n, int bits) {
    float min_val = data[0], max_val = data[0];
    for (int i = 1; i < n; i++) {
        if (data[i] < min_val) min_val = data[i];
        if (data[i] > max_val) max_val = data[i];
    }
    float range = max_val - min_val;
    if (range < 1e-10f) range = 1e-10f;
    int qmax = (1 << bits) - 1;
    float scale = range / qmax;
    float zero_point = min_val;
    return (QuantParams){scale, zero_point, bits};
}

// Quantize float32 to int8
void quantize_int8(const float* input, int8_t* output, int n, QuantParams* params) {
    *params = compute_quant_params(input, n, 8);
    float inv_scale = 1.0f / params->scale;
    for (int i = 0; i < n; i++) {
        float val = (input[i] - params->zero_point) * inv_scale;
        int q = (int)roundf(val);
        if (q < -128) q = -128;
        if (q > 127) q = 127;
        output[i] = (int8_t)q;
    }
}

// Dequantize int8 to float32
void dequantize_int8(const int8_t* input, float* output, int n, const QuantParams* params) {
    for (int i = 0; i < n; i++) {
        output[i] = (float)input[i] * params->scale + params->zero_point;
    }
}

// Quantize float32 to int4 (packed, 2 values per byte)
void quantize_int4(const float* input, uint8_t* output, int n, QuantParams* params) {
    *params = compute_quant_params(input, n, 4);
    float inv_scale = 1.0f / params->scale;
    for (int i = 0; i < n; i += 2) {
        float v0 = (input[i] - params->zero_point) * inv_scale;
        float v1 = (i + 1 < n) ? (input[i+1] - params->zero_point) * inv_scale : 0;
        int q0 = (int)roundf(v0); if (q0 < 0) q0 = 0; if (q0 > 15) q0 = 15;
        int q1 = (int)roundf(v1); if (q1 < 0) q1 = 0; if (q1 > 15) q1 = 15;
        output[i / 2] = (uint8_t)((q0 & 0x0F) | ((q1 & 0x0F) << 4));
    }
}

// Dequantize int4 packed to float32
void dequantize_int4(const uint8_t* input, float* output, int n, const QuantParams* params) {
    for (int i = 0; i < n; i += 2) {
        uint8_t packed = input[i / 2];
        output[i] = (float)(packed & 0x0F) * params->scale + params->zero_point;
        if (i + 1 < n) {
            output[i+1] = (float)((packed >> 4) & 0x0F) * params->scale + params->zero_point;
        }
    }
}

// Quantized int8 dot product (for attention score computation)
int32_t quantized_dot_int8(const int8_t* a, const int8_t* b, int n) {
    int32_t sum = 0;
    for (int i = 0; i < n; i++) {
        sum += (int32_t)a[i] * (int32_t)b[i];
    }
    return sum;
}

// Block quantization for transformer weights
void block_quantize_int8(const float* input, int8_t* output, float* scales, int n, int block_size) {
    int n_blocks = (n + block_size - 1) / block_size;
    for (int b = 0; b < n_blocks; b++) {
        int start = b * block_size;
        int end = start + block_size;
        if (end > n) end = n;
        int len = end - start;
        float absmax = 0;
        for (int i = start; i < end; i++) {
            float av = fabsf(input[i]);
            if (av > absmax) absmax = av;
        }
        scales[b] = absmax / 127.0f;
        float inv = (absmax > 1e-10f) ? 127.0f / absmax : 0.0f;
        for (int i = start; i < end; i++) {
            int q = (int)roundf(input[i] * inv);
            if (q < -128) q = -128;
            if (q > 127) q = 127;
            output[i] = (int8_t)q;
        }
    }
}
