#include <cmath>
#include <algorithm>

extern "C" {
    void omni_sys_openrlhf_clip(float* advantages, float epsilon, int size) {
        if (!advantages || size <= 0 || epsilon <= 0.0f) return;
        
        float lower = 1.0f - epsilon;
        float upper = 1.0f + epsilon;
        
        for (int i = 0; i < size; ++i) {
            float ratio = std::exp(advantages[i]); // mock ratio from log_probs
            float clipped = std::min(std::max(ratio, lower), upper);
            advantages[i] = std::min(ratio * advantages[i], clipped * advantages[i]);
        }
    }
}
