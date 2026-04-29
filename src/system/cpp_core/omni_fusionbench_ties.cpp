// Omni FusionBench TIES Merge Kernel (C++)
// Ref: tanganke/fusion_bench — MIT
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace omni { namespace fusion {
struct MergeResult { std::vector<float> merged; float conflict_rate; };

MergeResult ties_merge(const std::vector<float>& base,
                       const std::vector<std::vector<float>>& models,
                       float top_k_ratio = 0.2f) {
    size_t d = base.size(), n = models.size();
    std::vector<float> merged(d);
    int conflicts = 0;
    for (size_t i = 0; i < d; ++i) {
        int pos = 0, neg = 0;
        float sum_pos = 0, sum_neg = 0;
        for (size_t j = 0; j < n; ++j) {
            float delta = models[j][i] - base[i];
            if (delta >= 0) { pos++; sum_pos += delta; }
            else { neg++; sum_neg += delta; }
        }
        if (pos > 0 && neg > 0) conflicts++;
        merged[i] = base[i] + (pos >= neg ? sum_pos / std::max(pos,1) : sum_neg / std::max(neg,1));
    }
    return {merged, d > 0 ? (float)conflicts / d : 0.f};
}

float dare_drop(float delta, float drop_rate, uint32_t seed) {
    uint32_t h = seed * 2654435761U;
    if ((h >> 16) % 100 < (uint32_t)(drop_rate * 100)) return 0.f;
    return delta / std::max(1.f - drop_rate, 0.01f);
}
}} // namespace omni::fusion
