#include <cstdint>

extern "C" {
    // EdgeTTS fast pre-emphasis filter for audio synthesis
    void edgetts_apply_preemphasis(float* waveform, uint32_t length, float coeff) {
        if (length < 2) return;
        // Go backwards to avoid overwriting needed samples
        for (uint32_t i = length - 1; i > 0; --i) {
            waveform[i] = waveform[i] - coeff * waveform[i - 1];
        }
    }
}
