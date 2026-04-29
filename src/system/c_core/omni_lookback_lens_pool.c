/* Omni Lookback Lens Attention Pool (C)
 * System Layer: Bare-metal attention weight pooling.
 * Ref: voidism/Lookback-Lens — EMNLP 2024 */
#include <stddef.h>
float omni_lookback_ratio(const float* weights, size_t total, size_t ctx_len) {
    if (!weights || total == 0 || ctx_len == 0) return 0.0f;
    float ctx_sum = 0.0f, all_sum = 0.0f;
    size_t bound = ctx_len < total ? ctx_len : total;
    for (size_t i = 0; i < total; ++i) { all_sum += weights[i]; if (i < bound) ctx_sum += weights[i]; }
    return all_sum > 0.0f ? ctx_sum / all_sum : 0.0f;
}
