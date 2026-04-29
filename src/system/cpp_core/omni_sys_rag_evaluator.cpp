#include <cstdint>
#include <cmath>

// OMNI System Kernel: Mean Reciprocal Rank
extern "C" {
        double compute(const int32_t* ranks, int32_t len) {
            double mrr = 0.0;
            for(int i=0; i<len; i++) {
                if(ranks[i] > 0) mrr += 1.0 / ranks[i];
            }
            return len > 0 ? mrr / len : 0.0;
        }
}