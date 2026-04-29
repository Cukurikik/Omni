#include <cstdint>
#include <cmath>

// OMNI System Kernel: Dot product
extern "C" {
        double compute(const double* vec_a, const double* vec_b, int32_t len) {
            double dot = 0.0;
            for(int i=0; i<len; i++) dot += vec_a[i] * vec_b[i];
            return dot;
        }
}