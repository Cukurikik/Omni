#include <stdint.h>
#include <math.h>

extern "C" {

void omni_preprocess_image(
    const double* input_pixels, 
    int32_t width, 
    int32_t height, 
    double* out_pixels, 
    int32_t* err_code
) {
    if (!err_code) return;

    if (!input_pixels || !out_pixels || width <= 0 || height <= 0) {
        *err_code = -1;
        return;
    }

    int32_t total_pixels = width * height;

    // Deterministic mathematical implementation of standardization
    // Calculate mean and std deviation
    double sum = 0.0;
    for (int32_t i = 0; i < total_pixels; ++i) {
        sum += input_pixels[i];
    }
    double mean = sum / total_pixels;

    double sq_diff_sum = 0.0;
    for (int32_t i = 0; i < total_pixels; ++i) {
        double diff = input_pixels[i] - mean;
        sq_diff_sum += diff * diff;
    }
    double std_dev = sqrt(sq_diff_sum / total_pixels) + 1e-8; // avoid div by 0

    // Apply standardization
    for (int32_t i = 0; i < total_pixels; ++i) {
        out_pixels[i] = (input_pixels[i] - mean) / std_dev;
    }

    *err_code = 0;
}

}
