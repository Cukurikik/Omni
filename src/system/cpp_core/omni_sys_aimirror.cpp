#include <cmath>
extern "C" {
    float omni_sys_aimirror_feature_distance(const float* src, const float* tgt, int dim) {
        if (!src || !tgt || dim <= 0) return 0.0f;
        float sum = 0.0f;
        for (int i = 0; i < dim; ++i) { float d = src[i] - tgt[i]; sum += d * d; }
        return std::sqrt(sum);
    }
}
