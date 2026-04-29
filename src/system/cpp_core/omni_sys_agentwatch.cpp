#include <cstdint>

extern "C" {
    float omni_sys_agentwatch_moving_average(float new_val, float old_avg, int count) {
        if (count <= 0) return new_val;
        return old_avg + (new_val - old_avg) / (count + 1);
    }
}
