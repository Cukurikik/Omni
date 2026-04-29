#include <cstdint>
#include <cmath>

// OMNI System Kernel: MFCC pre-emphasis
extern "C" {
        double compute(double current_sample, double prev_sample) {
            double alpha = 0.97;
            return current_sample - alpha * prev_sample;
        }
}