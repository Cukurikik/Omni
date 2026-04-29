#include <cstdint>
#include <cmath>

// OMNI System Kernel: L2 Norm for gradient vectors
extern "C" {
        double compute(const double* grad, int32_t len) {
            double sum = 0.0;
            for(int i=0; i<len; i++) sum += grad[i] * grad[i];
            return std::sqrt(sum);
        }
}