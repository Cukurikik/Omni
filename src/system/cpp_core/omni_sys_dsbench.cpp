#include <cmath>

extern "C" {
    float omni_sys_dsbench_aggregate_score(const float* task_scores, int num_tasks) {
        if (!task_scores || num_tasks <= 0) return 0.0f;
        
        float sum = 0.0f;
        for (int i = 0; i < num_tasks; ++i) {
            sum += task_scores[i];
        }
        return (sum / num_tasks) * 100.0f; // Scale to 100
    }
}
