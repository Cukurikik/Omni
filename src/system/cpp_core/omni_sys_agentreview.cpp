#include <cstdint>

extern "C" {
    /// Compute reviewer confidence from agreement rate.
    float omni_sys_agentreview_confidence(int agree_count, int total_reviews) {
        if (total_reviews <= 0) return 0.0f;
        return (float)agree_count / (float)total_reviews;
    }

    /// Weighted review score aggregation.
    float omni_sys_agentreview_weighted_score(const float* scores, const float* weights, int n) {
        if (!scores || !weights || n <= 0) return 0.0f;
        float sum_w = 0.0f, sum_ws = 0.0f;
        for (int i = 0; i < n; ++i) {
            sum_ws += scores[i] * weights[i];
            sum_w += weights[i];
        }
        return (sum_w > 0.0f) ? sum_ws / sum_w : 0.0f;
    }
}
