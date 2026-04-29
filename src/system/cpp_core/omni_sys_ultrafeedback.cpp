#include <cmath>

extern "C" {
    float omni_sys_ultrafeedback_aggregate(const float* scores, int count) {
        if (!scores || count <= 0) return 0.0f;
        
        float sum = 0.0f;
        for (int i = 0; i < count; ++i) {
            sum += scores[i];
        }
        return sum / count;
    }
}
