#include <cmath>
extern "C" {
    float omni_sys_alan_sdk_vad_energy(const float* samples, int n) {
        if (!samples || n <= 0) return 0.0f;
        float rms = 0;
        for (int i = 0; i < n; ++i) rms += samples[i] * samples[i];
        return std::sqrt(rms / (float)n);
    }
}
