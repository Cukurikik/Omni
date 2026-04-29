#include <cmath>

extern "C" {
    void omni_sys_fastlora_scale_weights(float* weights, int size, float scale) {
        if (!weights || size <= 0) return;
        
        for (int i = 0; i < size; ++i) {
            weights[i] *= scale;
        }
    }
}
