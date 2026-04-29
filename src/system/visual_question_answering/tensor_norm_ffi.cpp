#include <stdint.h>
#include <math.h>

extern "C" {

// Fast FFI for image tensor normalization
// Crucial pre-processing step for Multimodal Vision Encoders (e.g., CLIP, ViT)
void omni_normalize_image_tensor(
    const uint8_t* rgb_pixels,
    int32_t num_pixels,
    const float* mean,  // Array of 3 floats [R, G, B]
    const float* std,   // Array of 3 floats [R, G, B]
    float* out_tensor,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!rgb_pixels || !mean || !std || !out_tensor || num_pixels <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution
    // Normalizes an RGB pixel array to a float tensor: (pixel/255.0 - mean) / std
    
    for (int32_t i = 0; i < num_pixels; ++i) {
        int32_t idx = i * 3; // Assuming interleaved RGB
        
        float r = (float)rgb_pixels[idx] / 255.0f;
        float g = (float)rgb_pixels[idx + 1] / 255.0f;
        float b = (float)rgb_pixels[idx + 2] / 255.0f;
        
        out_tensor[idx]     = (r - mean[0]) / std[0];
        out_tensor[idx + 1] = (g - mean[1]) / std[1];
        out_tensor[idx + 2] = (b - mean[2]) / std[2];
    }

    *err_code = 0;
}

}
