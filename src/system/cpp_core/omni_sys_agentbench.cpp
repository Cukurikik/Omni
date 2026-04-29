#include <cstdint>

extern "C" {
    float omni_sys_agentbench_compute_efficiency(int optimal_steps, int taken_steps) {
        if (optimal_steps <= 0 || taken_steps <= 0) return 0.0f;
        if (taken_steps <= optimal_steps) return 1.0f;
        
        // Efficiency decays as more steps are taken
        return (float)optimal_steps / (float)taken_steps;
    }
}
