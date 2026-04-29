#include <cmath>

extern "C" {
    void omni_sys_kgfit_transe_score(const float* head, const float* relation, const float* tail, float* out_score, int dim) {
        if (!head || !relation || !tail || !out_score || dim <= 0) return;
        
        float dist = 0.0f;
        for (int i = 0; i < dim; ++i) {
            float diff = head[i] + relation[i] - tail[i];
            dist += std::abs(diff); // L1 distance
        }
        *out_score = -dist; // Higher is better
    }
}
