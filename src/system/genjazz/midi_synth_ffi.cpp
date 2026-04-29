// OMNI SYSTEM LAYER: Generative Jazz (C++)
// FFI for high-speed sine wave synthesis from MIDI notes.

#include <vector>
#include <cmath>

extern "C" {

    const double PI = 3.141592653589793238460;

    // Convert MIDI note to Frequency
    double midi_to_freq(int midi_note) {
        return 440.0 * std::pow(2.0, (midi_note - 69) / 12.0);
    }

    // Synthesize a sequence of MIDI notes into PCM float array
    int omni_synth_midi(const int* midi_notes, int num_notes, double duration_sec, int sample_rate, float* out_buffer, int max_samples) {
        if (!midi_notes || !out_buffer || num_notes <= 0) return -1;

        int samples_per_note = (int)(duration_sec * sample_rate);
        int total_required = samples_per_note * num_notes;

        if (total_required > max_samples) return -2; // Buffer too small

        for (int i = 0; i < num_notes; ++i) {
            double freq = midi_to_freq(midi_notes[i]);
            int offset = i * samples_per_note;

            for (int s = 0; s < samples_per_note; ++s) {
                double time = (double)s / sample_rate;
                
                // Simple sine wave with ADSR envelope (triangle approx)
                double env = 1.0;
                if (s < 100) env = s / 100.0; // Attack
                if (s > samples_per_note - 100) env = (samples_per_note - s) / 100.0; // Release
                
                double val = std::sin(2.0 * PI * freq * time) * env;
                
                out_buffer[offset + s] = (float)val;
            }
        }

        return total_required; // Return number of written samples
    }
}
