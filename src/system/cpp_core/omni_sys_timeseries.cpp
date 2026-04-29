#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

extern "C" {
    void omni_sys_timeseries_dft(const float* real_in, float* real_out, float* imag_out, int n) {
        if (n <= 0) return;
        
        for (int k = 0; k < n; ++k) {
            real_out[k] = 0.0f;
            imag_out[k] = 0.0f;
            for (int t = 0; t < n; ++t) {
                float angle = 2.0f * M_PI * t * k / n;
                real_out[k] += real_in[t] * std::cos(angle);
                imag_out[k] -= real_in[t] * std::sin(angle);
            }
        }
    }
}
