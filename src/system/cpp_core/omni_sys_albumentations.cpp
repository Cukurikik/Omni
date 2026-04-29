#include <cmath>
extern "C" {
    void omni_sys_albumentations_normalize(float* pixels, int n, float mean, float std_dev) {
        if (!pixels || n <= 0 || std_dev <= 0.0f) return;
        for (int i = 0; i < n; ++i) pixels[i] = (pixels[i] - mean) / std_dev;
    }
    void omni_sys_albumentations_flip_h(float* row, int width) {
        if (!row || width <= 0) return;
        for (int i = 0; i < width / 2; ++i) {
            float tmp = row[i]; row[i] = row[width - 1 - i]; row[width - 1 - i] = tmp;
        }
    }
}
