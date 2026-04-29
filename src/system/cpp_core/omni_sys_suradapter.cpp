#include <cmath>

extern "C" {
    void omni_sys_suradapter_clip_latents(float* latents, int size, float min_val, float max_val) {
        if (!latents || size <= 0) return;
        
        for (int i = 0; i < size; ++i) {
            if (latents[i] < min_val) latents[i] = min_val;
            if (latents[i] > max_val) latents[i] = max_val;
        }
    }
}
