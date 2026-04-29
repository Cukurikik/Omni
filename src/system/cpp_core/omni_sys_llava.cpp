#include <cstdint>

extern "C" {
    void omni_sys_llava_roi_pool(const float* feature_map, float* output, int x, int y, int w, int h, int map_width) {
        if (!feature_map || !output || w <= 0 || h <= 0) return;
        
        // Mock ROI pooling - average pooling
        float sum = 0.0f;
        for (int i = y; i < y + h; ++i) {
            for (int j = x; j < x + w; ++j) {
                sum += feature_map[i * map_width + j];
            }
        }
        output[0] = sum / (w * h);
    }
}
