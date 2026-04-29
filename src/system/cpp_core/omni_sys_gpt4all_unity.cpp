#include <cstdint>
#include <cmath>

// OMNI System Kernel: Quaternion magnitude
extern "C" {
        double compute(double x, double y, double z, double w) {
            return std::sqrt(x*x + y*y + z*z + w*w);
        }
}