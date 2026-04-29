#include <stdint.h>

extern "C" {

// Fast FFI for simulating basic computer vision morphological operations
// Used to dilate text pixels to form continuous blocks for layout detection
void omni_morph_dilate_1d(
    const uint8_t* image_row,
    int32_t row_len,
    int32_t kernel_size,
    uint8_t* out_row,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!image_row || !out_row || row_len <= 0 || kernel_size <= 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution of 1D Dilation
    int32_t k_half = kernel_size / 2;

    for (int32_t i = 0; i < row_len; ++i) {
        uint8_t local_max = 0;
        
        int32_t start = (i - k_half < 0) ? 0 : i - k_half;
        int32_t end = (i + k_half >= row_len) ? row_len - 1 : i + k_half;
        
        for (int32_t j = start; j <= end; ++j) {
            if (image_row[j] > local_max) {
                local_max = image_row[j];
            }
        }
        
        out_row[i] = local_max;
    }

    *err_code = 0;
}

}
