#include <cmath>
extern "C" {
    float omni_sys_anime4k_bicubic_weight(float x) {
        float ax = std::fabs(x);
        if (ax <= 1.0f) return (1.5f * ax - 2.5f) * ax * ax + 1.0f;
        if (ax <= 2.0f) return ((-0.5f * ax + 2.5f) * ax - 4.0f) * ax + 2.0f;
        return 0.0f;
    }
}
