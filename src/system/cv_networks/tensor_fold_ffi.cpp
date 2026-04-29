#include <cstdint>

extern "C" {

void omni_tensor_fold_2d(
    const float* input_tensor, 
    int32_t width, 
    int32_t height, 
    int32_t channels, 
    int32_t patch_h, 
    int32_t patch_w, 
    float* out_folded, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!input_tensor || !out_folded || width <= 0 || height <= 0 || channels <= 0 || patch_h <= 0 || patch_w <= 0) {
        *err_code = -1;
        return;
    }

    if (height % patch_h != 0 || width % patch_w != 0) {
        *err_code = -2; // Spatial dimensions must be divisible by patch size
        return;
    }

    int32_t num_patches_h = height / patch_h;
    int32_t num_patches_w = width / patch_w;
    int32_t patch_area = patch_h * patch_w;

    // Mathematical unfold/fold simulation for ViT patch extraction
    // Transforms [H, W, C] -> [N, P, C] where N=num_patches, P=patch_area
    
    int32_t out_idx = 0;

    for (int32_t ph = 0; ph < num_patches_h; ++ph) {
        for (int32_t pw = 0; pw < num_patches_w; ++pw) {
            
            // For each patch, extract its pixels
            for (int32_t y = 0; y < patch_h; ++y) {
                for (int32_t x = 0; x < patch_w; ++x) {
                    
                    int32_t orig_y = ph * patch_h + y;
                    int32_t orig_x = pw * patch_w + x;
                    
                    for (int32_t c = 0; c < channels; ++c) {
                        int32_t in_idx = (orig_y * width * channels) + (orig_x * channels) + c;
                        out_folded[out_idx++] = input_tensor[in_idx];
                    }
                }
            }
        }
    }

    *err_code = 0;
}

}
