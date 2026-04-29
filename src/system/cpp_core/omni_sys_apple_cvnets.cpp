#include <cmath>
extern "C" {
    float omni_sys_apple_cvnets_gelu(float x) {
        return 0.5f * x * (1.0f + std::tanh(0.7978846f * (x + 0.044715f * x * x * x)));
    }
    float omni_sys_apple_cvnets_layer_norm(float val, float mean, float var, float gamma, float beta) {
        return gamma * (val - mean) / std::sqrt(var + 1e-5f) + beta;
    }
}
