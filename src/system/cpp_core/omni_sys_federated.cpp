#include <cstdint>

extern "C" {
    // Federated learning fast gradient clipping
    void federated_clip_gradients(float* gradients, uint32_t count, float max_norm) {
        float sum_sq = 0.0f;
        for (uint32_t i = 0; i < count; ++i) {
            sum_sq += gradients[i] * gradients[i];
        }
        
        float norm = __builtin_sqrtf(sum_sq);
        if (norm > max_norm && norm > 0.0f) {
            float scale = max_norm / norm;
            for (uint32_t i = 0; i < count; ++i) {
                gradients[i] *= scale;
            }
        }
    }
}
