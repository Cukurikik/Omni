#include <cstdint>

extern "C" {
    float omni_sys_minigpt4_attention_mock(const float* q, const float* k, int dim) {
        if (!q || !k || dim <= 0) return 0.0f;
        
        float dot = 0.0f;
        for (int i = 0; i < dim; ++i) {
            dot += q[i] * k[i];
        }
        return dot; // Unscaled
    }
}
