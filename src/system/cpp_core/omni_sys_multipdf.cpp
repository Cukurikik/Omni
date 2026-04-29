#include <cmath>

extern "C" {
    float omni_sys_multipdf_faiss_l2(const float* vec_a, const float* vec_b, int dim) {
        if (!vec_a || !vec_b || dim <= 0) return 0.0f;
        
        float dist = 0.0f;
        for (int i = 0; i < dim; ++i) {
            float diff = vec_a[i] - vec_b[i];
            dist += diff * diff;
        }
        return std::sqrt(dist);
    }
}
