#include <cmath>

extern "C" {
    void omni_sys_halc_apply_focal_penalty(float* logits, int size, float penalty) {
        if (!logits || size <= 0) return;
        
        for (int i = 0; i < size; ++i) {
            // Mock focal penalty applied to highly confident tokens
            if (logits[i] > 10.0f) {
                logits[i] -= penalty;
            }
        }
    }
}
