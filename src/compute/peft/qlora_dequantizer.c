#include <stdint.h>
#include <math.h>

// OMNI PEFT: QLoRA NormalFloat4 Dequantizer
// Low-level C implementation for expanding 4-bit NF4 quantized weights back to FP16 
// during the forward pass for Parameter Efficient Fine-Tuning.
// Source: huggingface/peft (bitsandbytes mechanics)

typedef enum {
    DEQUANT_SUCCESS = 0,
    DEQUANT_ERR_NULL = 1
} dequant_err_t;

// The Standard NormalFloat4 (NF4) lookup table mapping 4-bit integers (0-15) to FP32 values.
// These values are statistically derived to have equal area under the standard normal distribution.
static const float NF4_LUT[16] = {
    -1.0f, -0.6961928009986877f, -0.5250730514526367f, -0.39491748809814453f,
    -0.28444138169288635f, -0.18477343022823334f, -0.09105003625154495f, 0.0f,
    0.07958029955625534f, 0.16093020141124725f, 0.24611230194568634f, 0.33791524171829224f,
    0.44070982933044434f, 0.5626170039176941f, 0.7229568362236023f, 1.0f
};

/**
 * Dequantizes a block of NF4 packed bytes back into a float array.
 * packed_data: Array of 8-bit integers, where each byte contains two 4-bit NF4 values.
 * absmax: The absolute maximum scaling factor for this quantization block.
 * out_fp32: Pre-allocated float array of size (num_bytes * 2).
 */
dequant_err_t dequantize_nf4_block(
    const uint8_t* packed_data, 
    float absmax, 
    int num_bytes, 
    float* out_fp32) 
{
    if (!packed_data || !out_fp32) return DEQUANT_ERR_NULL;

    for (int i = 0; i < num_bytes; ++i) {
        uint8_t byte = packed_data[i];
        
        // Extract lower 4 bits
        uint8_t idx1 = byte & 0x0F;
        // Extract upper 4 bits
        uint8_t idx2 = (byte >> 4) & 0x0F;

        // Map through LUT and apply scale
        out_fp32[i * 2]     = NF4_LUT[idx1] * absmax;
        out_fp32[i * 2 + 1] = NF4_LUT[idx2] * absmax;
    }

    return DEQUANT_SUCCESS;
}
