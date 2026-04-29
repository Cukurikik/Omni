#include <cmath>

extern "C" {
    void omni_sys_ragfusion_normalize_scores(float* scores, int size) {
        if (!scores || size <= 0) return;
        
        float max_val = 0.0f;
        for (int i = 0; i < size; ++i) {
            if (scores[i] > max_val) max_val = scores[i];
        }
        
        if (max_val > 0.0f) {
            for (int i = 0; i < size; ++i) {
                scores[i] /= max_val;
            }
        }
    }
}
