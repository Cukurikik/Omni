#include <cstdint>
#include <cmath>

extern "C" {
    // OMNI System Layer - Root Mean Square for Acoustic Waveforms
    double compute_waveform_rms(const double* wave, int32_t len) {
        if (!wave || len <= 0) return 0.0;
        double sum_sq = 0.0;
        for(int32_t i=0; i<len; i++) {
            sum_sq += wave[i] * wave[i];
        }
        return std::sqrt(sum_sq / len);
    }
}
