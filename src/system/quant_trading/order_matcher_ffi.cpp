#include <stdint.h>

extern "C" {

double omni_calculate_vwap(const double* prices, const double* volumes, int32_t length, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (!prices || !volumes || length <= 0) {
        *err_code = -1;
        return 0.0;
    }

    double cumulative_tp_v = 0.0; // Typical Price * Volume
    double cumulative_v = 0.0;    // Volume

    for (int32_t i = 0; i < length; i++) {
        if (prices[i] < 0.0 || volumes[i] < 0.0) {
            *err_code = -2;
            return 0.0;
        }
        cumulative_tp_v += prices[i] * volumes[i];
        cumulative_v += volumes[i];
    }

    if (cumulative_v == 0.0) {
        *err_code = -3;
        return 0.0;
    }

    *err_code = 0;
    return cumulative_tp_v / cumulative_v;
}

}
