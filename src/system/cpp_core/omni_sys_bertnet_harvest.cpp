#include <cstdint>
#include <cmath>

// OMNI System Kernel: Jaccard similarity
extern "C" {
        double compute(const int32_t* set_a, int32_t len_a, const int32_t* set_b, int32_t len_b) {
            int intersection = 0;
            for(int i=0; i<len_a; i++) {
                for(int j=0; j<len_b; j++) {
                    if(set_a[i] == set_b[j]) { intersection++; break; }
                }
            }
            int union_sz = len_a + len_b - intersection;
            return union_sz == 0 ? 0 : (double)intersection / union_sz;
        }
}