#include <cmath>

extern "C" {

    struct OmniPitchResult {
        int midi_pitch;
        double frequency_hz;
        const char* error;
    };

    void omni_free_pitch_result(OmniPitchResult* res) {
        if (res) delete res;
    }

    // High-performance frequency to MIDI mathematical conversion
    OmniPitchResult* freq_to_midi(double frequency) {
        OmniPitchResult* result = new OmniPitchResult{0, frequency, nullptr};

        if (frequency <= 0.0) {
            result->error = "Frequency must be strictly positive";
            return result;
        }

        // Mathematical conversion: p = 69 + 12 * log2(f / 440)
        double pitch_exact = 69.0 + 12.0 * std::log2(frequency / 440.0);
        int midi_pitch = static_cast<int>(std::round(pitch_exact));

        // Clamping to MIDI bounds [0, 127]
        if (midi_pitch < 0) midi_pitch = 0;
        if (midi_pitch > 127) midi_pitch = 127;

        result->midi_pitch = midi_pitch;
        return result;
    }
}
