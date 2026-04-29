#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - Fast Quaternion Magnitude Calculation
    double compute_quat_magnitude(double w, double x, double y, double z) {
        return std::sqrt(w*w + x*x + y*y + z*z);
    }
}
