#include <cmath>

extern "C" {
    float omni_sys_lqauto_mse(const float* original, const float* reconstructed, int size) {
        if (!original || !reconstructed || size <= 0) return 0.0f;
        
        float mse = 0.0f;
        for (int i = 0; i < size; ++i) {
            float diff = original[i] - reconstructed[i];
            mse += diff * diff;
        }
        return mse / size;
    }
}
