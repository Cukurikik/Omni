#include <cstdint>
#include <cmath>

// OMNI System Kernel: Acoustic wave root mean square
extern "C" {
        double compute(const double* signal, int32_t len) {
            double sum = 0.0;
            for(int i=0; i<len; i++) sum += signal[i] * signal[i];
            return std::sqrt(sum / len);
        }
}