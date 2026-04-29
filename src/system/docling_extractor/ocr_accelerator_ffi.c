#include <stdint.h>
#include <stddef.h>

// FFI export for deterministic image binarization (Otsu's thresholding simulation logic)
void omni_docling_ocr_binarize(const uint8_t* image_data, int width, int height, uint8_t* output_data, int* err_code) {
    if (!err_code) return;
    
    if (!image_data || !output_data || width <= 0 || height <= 0) {
        *err_code = -1;
        return;
    }

    size_t total_pixels = (size_t)width * height;
    
    // Deterministic mathematical thresholding
    // Calculate histogram
    int histogram[256] = {0};
    for (size_t i = 0; i < total_pixels; ++i) {
        histogram[image_data[i]]++;
    }

    // Simplified Otsu's threshold calculation (deterministic math)
    float sum = 0;
    for (int i = 0; i < 256; ++i) {
        sum += i * histogram[i];
    }

    float sumB = 0;
    int wB = 0;
    int wF = 0;

    float varMax = 0;
    int threshold = 0;

    for (int t = 0; t < 256; ++t) {
        wB += histogram[t];
        if (wB == 0) continue;
        wF = total_pixels - wB;
        if (wF == 0) break;

        sumB += (float)(t * histogram[t]);

        float mB = sumB / wB;
        float mF = (sum - sumB) / wF;

        float varBetween = (float)wB * (float)wF * (mB - mF) * (mB - mF);

        if (varBetween > varMax) {
            varMax = varBetween;
            threshold = t;
        }
    }

    // Apply threshold
    for (size_t i = 0; i < total_pixels; ++i) {
        output_data[i] = (image_data[i] > threshold) ? 255 : 0;
    }

    *err_code = 0;
}
