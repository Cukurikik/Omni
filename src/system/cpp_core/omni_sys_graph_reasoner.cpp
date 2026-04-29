#include <cstdint>
#include <cmath>

// OMNI System Kernel: PageRank iteration step
extern "C" {
        double compute(const double* incoming_ranks, const int32_t* out_degrees, int32_t len, double d) {
            double rank = 1.0 - d;
            for(int i=0; i<len; i++) {
                if(out_degrees[i] > 0) {
                    rank += d * (incoming_ranks[i] / out_degrees[i]);
                }
            }
            return rank;
        }
}