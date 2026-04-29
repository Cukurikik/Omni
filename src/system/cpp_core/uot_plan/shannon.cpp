#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - Shannon Entropy
    double compute_shannon_entropy(const double* probs, int32_t len) {
        if (!probs || len <= 0) return 0.0;
        double entropy = 0.0;
        for(int32_t i=0; i<len; ++i) {
            if (probs[i] > 0.0) {
                entropy -= probs[i] * std::log2(probs[i]);
            }
        }
        return entropy;
    }
}
