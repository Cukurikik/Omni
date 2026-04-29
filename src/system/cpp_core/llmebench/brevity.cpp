#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - Bleu Score Brevity Penalty
    double compute_brevity_penalty(int32_t candidate_len, int32_t reference_len) {
        if (candidate_len > reference_len) return 1.0;
        if (candidate_len == 0) return 0.0;
        return std::exp(1.0 - ((double)reference_len / candidate_len));
    }
}
