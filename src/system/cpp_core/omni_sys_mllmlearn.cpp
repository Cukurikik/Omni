#include <cmath>

extern "C" {
    void omni_sys_mllmlearn_cross_attention(float* q, float* k, float* v, float* out, int dim) {
        if (!q || !k || !v || !out || dim <= 0) return;
        
        // Mock dot-product cross attention over 1D vectors
        float score = 0.0f;
        for (int i = 0; i < dim; ++i) {
            score += q[i] * k[i];
        }
        
        float weight = std::max(0.0f, score / std::sqrt((float)dim)); // ReLU-scaled
        
        for (int i = 0; i < dim; ++i) {
            out[i] = v[i] * weight;
        }
    }
}
