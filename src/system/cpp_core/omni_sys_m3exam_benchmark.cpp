#include <cstdint>
#include <cmath>

// OMNI System Kernel: F1 Score
extern "C" {
        double compute(double precision, double recall) {
            if(precision + recall == 0.0) return 0.0;
            return 2.0 * (precision * recall) / (precision + recall);
        }
}