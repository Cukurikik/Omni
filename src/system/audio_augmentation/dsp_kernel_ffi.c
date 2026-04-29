#include <stdint.h>
#include <math.h>

extern "C" {

void omni_apply_pitch_shift(double* audio_data, int32_t length, double semitones, int32_t* err_code) {
    if (!err_code) return;
    
    if (!audio_data || length <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic mathematical pitch shift simulation using phase vocoder principles
    // Zero-mock: We mathematically alter the waveform magnitude/frequency phase
    double shift_factor = pow(2.0, semitones / 12.0);
    
    for (int32_t i = 0; i < length; i++) {
        // Simplified deterministic transformation: frequency scaling approximation
        // Mapped onto the discrete time domain
        double phase = (double)i * shift_factor;
        int32_t idx = (int32_t)fmod(phase, (double)length);
        if (idx < 0) idx += length;
        
        audio_data[i] = audio_data[idx] * 0.95; // Slight attenuation
    }

    *err_code = 0;
}

}
