#include <cstdint>
#include <cmath>

// OMNI System Kernel: Gini impurity
extern "C" {
        double compute(const double* probabilities, int32_t len) {
            double sum = 0.0;
            for(int i=0; i<len; i++) sum += probabilities[i] * probabilities[i];
            return 1.0 - sum;
        }
}