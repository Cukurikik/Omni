#include <cstdint>
#include <cmath>
#include <vector>

extern "C" {
    // Salmonn audio magnitude extraction (simplified FFT magnitude concept)
    void extract_audio_magnitude(const float* waveform, uint32_t length, float* out_magnitude, uint32_t frame_size) {
        if (frame_size == 0) return;
        
        uint32_t num_frames = length / frame_size;
        for (uint32_t i = 0; i < num_frames; ++i) {
            float energy = 0.0f;
            for (uint32_t j = 0; j < frame_size; ++j) {
                float sample = waveform[i * frame_size + j];
                energy += sample * sample;
            }
            out_magnitude[i] = std::sqrt(energy / frame_size);
        }
    }
}
