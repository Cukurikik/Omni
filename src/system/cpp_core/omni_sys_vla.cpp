#include <cmath>

extern "C" {
    void omni_sys_vla_normalize_action(float* actions, int dim) {
        if (!actions || dim <= 0) return;
        
        float max_val = 0.0f;
        for (int i = 0; i < dim; ++i) {
            float abs_val = std::abs(actions[i]);
            if (abs_val > max_val) max_val = abs_val;
        }
        
        if (max_val > 0.0f) {
            for (int i = 0; i < dim; ++i) {
                actions[i] /= max_val;
            }
        }
    }
}
