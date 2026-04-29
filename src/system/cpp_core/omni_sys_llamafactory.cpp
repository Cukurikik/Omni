#include <cmath>

extern "C" {
    float omni_sys_llamafactory_loss_decay(float initial_loss, int step, float decay_rate) {
        // Mock exponential decay for training loss curves
        return initial_loss * std::exp(-decay_rate * step);
    }
}
