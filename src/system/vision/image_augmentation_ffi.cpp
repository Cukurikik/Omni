#include <cstdint>
#include <cstdlib>
#include <algorithm>

enum class OmniStatus {
    OK = 0,
    NULL_POINTER = 1,
    INVALID_DIMS = 2
};

struct OmniImageResult {
    uint8_t* data;
    int width;
    int height;
    int channels;
    OmniStatus status;
};

extern "C" {

    // Simulates fast C++ image cropping via raw memory manipulation for FFI boundaries
    // Image is expected in HWC (Height, Width, Channels) format, contiguous.
    __attribute__((visibility("default")))
    OmniImageResult omni_random_crop(
        const uint8_t* img_data, 
        int width, int height, int channels,
        int crop_width, int crop_height,
        int start_x, int start_y // Seeded from Go/Python caller
    ) {
        if (!img_data) return {nullptr, 0, 0, 0, OmniStatus::NULL_POINTER};
        
        if (crop_width > width || crop_height > height || 
            start_x < 0 || start_y < 0 || 
            start_x + crop_width > width || start_y + crop_height > height) {
            return {nullptr, 0, 0, 0, OmniStatus::INVALID_DIMS};
        }

        int row_stride = width * channels;
        int crop_row_stride = crop_width * channels;
        
        uint8_t* out_data = (uint8_t*)malloc(crop_width * crop_height * channels);
        if (!out_data) return {nullptr, 0, 0, 0, OmniStatus::NULL_POINTER};

        for (int y = 0; y < crop_height; ++y) {
            const uint8_t* src_row = img_data + ((start_y + y) * row_stride) + (start_x * channels);
            uint8_t* dst_row = out_data + (y * crop_row_stride);
            std::copy(src_row, src_row + crop_row_stride, dst_row);
        }

        return {out_data, crop_width, crop_height, channels, OmniStatus::OK};
    }

    __attribute__((visibility("default")))
    OmniImageResult omni_horizontal_flip(
        const uint8_t* img_data, 
        int width, int height, int channels
    ) {
        if (!img_data) return {nullptr, 0, 0, 0, OmniStatus::NULL_POINTER};

        int row_stride = width * channels;
        uint8_t* out_data = (uint8_t*)malloc(width * height * channels);
        if (!out_data) return {nullptr, 0, 0, 0, OmniStatus::NULL_POINTER};

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int src_idx = (y * row_stride) + (x * channels);
                int dst_idx = (y * row_stride) + ((width - 1 - x) * channels);
                for (int c = 0; c < channels; ++c) {
                    out_data[dst_idx + c] = img_data[src_idx + c];
                }
            }
        }

        return {out_data, width, height, channels, OmniStatus::OK};
    }

    __attribute__((visibility("default")))
    void omni_free_image(uint8_t* ptr) {
        if (ptr) free(ptr);
    }
}
