#include <cstdint>

extern "C" {
    float omni_sys_hallucination_penalty(int factual_mismatches, int total_claims) {
        if (total_claims <= 0) return 0.0f;
        
        float penalty = (float)factual_mismatches / (float)total_claims;
        // Exponential amplification of penalty
        return penalty * penalty;
    }
}
