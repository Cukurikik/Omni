#include <cmath>

extern "C" {
    void omni_sys_gptsovits_apply_window(float* signal, int size) {
        if (!signal || size <= 0) return;
        
        // Apply Hanning window
        for (int i = 0; i < size; ++i) {
            float multiplier = 0.5f * (1.0f - std::cos(2.0f * M_PI * i / (size - 1)));
            signal[i] *= multiplier;
        }
    }
}
