#include <cstdint>
extern "C" {
    float omni_sys_aro_bow_recall(int correct_matches, int total_queries) {
        if (total_queries <= 0) return 0.0f;
        return (float)correct_matches / (float)total_queries;
    }
    float omni_sys_aro_bow_mrr(const int* ranks, int n) {
        if (!ranks || n <= 0) return 0.0f;
        float sum = 0.0f;
        for (int i = 0; i < n; ++i) if (ranks[i] > 0) sum += 1.0f / (float)ranks[i];
        return sum / (float)n;
    }
}
