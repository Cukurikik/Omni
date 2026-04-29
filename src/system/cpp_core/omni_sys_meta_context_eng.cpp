#include <cstdint>
#include <cmath>

// OMNI System Kernel: Levenshtein distance simplified
extern "C" {
        int32_t compute(const uint8_t* a, int32_t len_a, const uint8_t* b, int32_t len_b) {
            int32_t diff = 0;
            int32_t min_len = len_a < len_b ? len_a : len_b;
            for(int i=0; i<min_len; i++) {
                if(a[i] != b[i]) diff++;
            }
            return diff + (len_a > len_b ? len_a - len_b : len_b - len_a);
        }
}