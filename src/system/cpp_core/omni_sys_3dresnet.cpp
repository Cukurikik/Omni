#include <cstdint>
extern "C" {
    float omni_sys_3dresnet_avg_pool_3d(const float* volume, int T, int H, int W) {
        if (!volume || T <= 0 || H <= 0 || W <= 0) return 0.0f;
        float sum = 0; int n = T * H * W;
        for (int i = 0; i < n; ++i) sum += volume[i];
        return sum / (float)n;
    }
}
