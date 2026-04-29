#include <stdint.h>
#include <math.h>

extern "C" {

void omni_rolling_window_stats(const double* data, int32_t length, int32_t window_size, double* out_mean, double* out_std, int32_t* err_code) {
    if (!err_code) return;
    
    if (!data || !out_mean || !out_std || length <= 0 || window_size <= 0 || window_size > length) {
        *err_code = -1;
        return;
    }

    // Calculate rolling window statistics mathematically
    double sum = 0.0;
    for (int32_t i = length - window_size; i < length; i++) {
        sum += data[i];
    }
    double mean = sum / window_size;

    double sq_diff_sum = 0.0;
    for (int32_t i = length - window_size; i < length; i++) {
        double diff = data[i] - mean;
        sq_diff_sum += diff * diff;
    }
    double std_dev = sqrt(sq_diff_sum / window_size);

    *out_mean = mean;
    *out_std = std_dev;
    *err_code = 0;
}

}
