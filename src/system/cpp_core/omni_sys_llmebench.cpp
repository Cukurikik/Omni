#include <cstdint>
#include <cmath>

// OMNI System Kernel: BLEU score brevity penalty
extern "C" {
        double compute(int32_t translation_len, int32_t reference_len) {
            if(translation_len > reference_len) return 1.0;
            if(translation_len == 0) return 0.0;
            return std::exp(1.0 - (double)reference_len / translation_len);
        }
}