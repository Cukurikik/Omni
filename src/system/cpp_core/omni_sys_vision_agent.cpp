#include <cstdint>
#include <cmath>

// OMNI System Kernel: Sobel magnitude
extern "C" {
        double compute(double gx, double gy) {
            return std::sqrt(gx*gx + gy*gy);
        }
}