#include <cstdint>
#include <cmath>

// OMNI System Kernel: Shannon Entropy
extern "C" {
        double compute(const double* probs, int32_t len) {
            double entropy = 0.0;
            for(int i=0; i<len; i++) {
                if(probs[i] > 0) entropy -= probs[i] * std::log2(probs[i]);
            }
            return entropy;
        }
}