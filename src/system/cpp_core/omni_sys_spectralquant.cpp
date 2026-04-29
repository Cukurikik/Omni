#include <cmath>

extern "C" {
    void omni_sys_spectralquant_apply_mask(float* matrix, const int* mask, int size) {
        if (!matrix || !mask || size <= 0) return;
        
        // Zero out elements where mask is 0
        for (int i = 0; i < size; ++i) {
            if (mask[i] == 0) {
                matrix[i] = 0.0f;
            }
        }
    }
}
