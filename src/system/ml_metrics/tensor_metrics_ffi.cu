#include <stdint.h>

extern "C" {

double omni_compute_accuracy(int32_t correct, int32_t total, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (total <= 0) {
        *err_code = -1;
        return 0.0;
    }
    
    if (correct < 0 || correct > total) {
        *err_code = -2;
        return 0.0;
    }

    *err_code = 0;
    return (double)correct / (double)total;
}

}
