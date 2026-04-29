#include <cstdint>

extern "C" {
    /// Compute inter-annotator agreement (Cohen's Kappa approximation).
    float omni_sys_argilla_cohen_kappa(int agree, int total, float p_e) {
        if (total <= 0) return 0.0f;
        float p_o = (float)agree / (float)total;
        if (p_e >= 1.0f) return 0.0f;
        return (p_o - p_e) / (1.0f - p_e);
    }

    /// Hash annotation ID for deterministic dedup.
    uint32_t omni_sys_argilla_hash_id(const char* id, int len) {
        uint32_t h = 2166136261u;
        for (int i = 0; i < len; ++i) {
            h ^= (uint8_t)id[i];
            h *= 16777619u;
        }
        return h;
    }
}
