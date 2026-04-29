#include <cmath>
extern "C" {
    float omni_sys_actionclip_temporal_pool(const float* feats, int T, int D, int t_idx) {
        if (!feats || T <= 0 || D <= 0 || t_idx < 0 || t_idx >= D) return 0.0f;
        float sum = 0.0f;
        for (int t = 0; t < T; ++t) sum += feats[t * D + t_idx];
        return sum / (float)T;
    }
}
