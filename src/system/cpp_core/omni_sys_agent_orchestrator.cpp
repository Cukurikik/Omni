#include <cmath>
extern "C" {
    float omni_sys_agent_orchestrator_load_balance(const float* loads, int n) {
        if (!loads || n <= 0) return 0.0f;
        float min_load = loads[0]; int min_idx = 0;
        for (int i = 1; i < n; ++i) if (loads[i] < min_load) { min_load = loads[i]; min_idx = i; }
        return (float)min_idx;
    }
}
