#include <cmath>

extern "C" {
    void omni_sys_internvl_normalize(float* vector, int dim) {
        if (!vector || dim <= 0) return;
        
        float sum_sq = 0.0f;
        for (int i = 0; i < dim; ++i) {
            sum_sq += vector[i] * vector[i];
        }
        
        float norm = std::sqrt(sum_sq);
        if (norm > 0.0f) {
            for (int i = 0; i < dim; ++i) {
                vector[i] /= norm;
            }
        }
    }
}
