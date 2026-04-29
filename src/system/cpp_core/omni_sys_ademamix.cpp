#include <cmath>
extern "C" {
    float omni_sys_ademamix_momentum(float grad, float m1, float m2, float beta1, float beta2, float alpha) {
        float new_m1 = beta1 * m1 + (1.0f - beta1) * grad;
        float new_m2 = beta2 * m2 + (1.0f - beta2) * grad;
        return alpha * new_m1 + (1.0f - alpha) * new_m2;
    }
}
