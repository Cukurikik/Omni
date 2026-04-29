#include <stdint.h>
#include <math.h>

extern "C" {

double omni_compute_entropy_kernel(const double* probs, int32_t length, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (!probs || length <= 0) {
        *err_code = -1;
        return 0.0;
    }

    double entropy = 0.0;
    for (int32_t i = 0; i < length; i++) {
        double p = probs[i];
        if (p < 0.0 || p > 1.0) {
            *err_code = -2;
            return 0.0;
        }
        if (p > 0.0) {
            entropy -= p * log2(p);
        }
    }

    *err_code = 0;
    return entropy;
}

}
