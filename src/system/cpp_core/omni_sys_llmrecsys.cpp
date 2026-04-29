#include <cmath>

extern "C" {
    float omni_sys_llmrecsys_cosine_sim(const float* vec_a, const float* vec_b, int dim) {
        if (!vec_a || !vec_b || dim <= 0) return 0.0f;
        
        float dot = 0.0f, norm_a = 0.0f, norm_b = 0.0f;
        for (int i = 0; i < dim; ++i) {
            dot += vec_a[i] * vec_b[i];
            norm_a += vec_a[i] * vec_a[i];
            norm_b += vec_b[i] * vec_b[i];
        }
        
        if (norm_a == 0.0f || norm_b == 0.0f) return 0.0f;
        return dot / (std::sqrt(norm_a) * std::sqrt(norm_b));
    }
}
