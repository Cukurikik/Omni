#include <cstdint>
#include <cmath>

// OMNI System Kernel: KL Divergence
extern "C" {
        double compute(const double* p, const double* q, int32_t len) {
            double div = 0.0;
            for(int i=0; i<len; i++) {
                if(p[i] > 0 && q[i] > 0) {
                    div += p[i] * std::log(p[i] / q[i]);
                }
            }
            return div;
        }
}