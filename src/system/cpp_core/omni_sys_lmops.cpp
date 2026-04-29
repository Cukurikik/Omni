#include <cmath>

extern "C" {
    float omni_sys_lmops_compute_gradient(float prev_loss, float current_loss) {
        // Mock finite difference gradient for prompt embedding space
        float diff = prev_loss - current_loss;
        return (diff > 0.0f) ? std::log(1.0f + diff) : -std::log(1.0f - diff);
    }
}
