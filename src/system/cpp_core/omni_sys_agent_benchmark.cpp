#include <cstdint>
extern "C" {
    float omni_sys_agent_benchmark_success_rate(int successes, int total) {
        if (total <= 0) return 0.0f;
        return (float)successes / (float)total;
    }
    float omni_sys_agent_benchmark_avg_steps(const int* steps, int n) {
        if (!steps || n <= 0) return 0.0f;
        int sum = 0; for (int i = 0; i < n; ++i) sum += steps[i];
        return (float)sum / (float)n;
    }
}
