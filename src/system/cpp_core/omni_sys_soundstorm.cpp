#include <cstdint>

extern "C" {
    void omni_sys_soundstorm_masking(int* tokens, int size, float mask_ratio) {
        if (!tokens || size <= 0 || mask_ratio <= 0.0f) return;
        
        int mask_count = (int)(size * mask_ratio);
        
        // Deterministic masking pattern based on prime stride
        int stride = 7; 
        for (int i = 0; i < mask_count; ++i) {
            int idx = (i * stride) % size;
            tokens[idx] = -1; // -1 indicates [MASK]
        }
    }
}
