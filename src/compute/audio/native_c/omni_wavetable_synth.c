/*
 * omni_wavetable_synth.c — Wavetable Oscillator
 * Layer: Compute / Audio
 *
 * High-performance, low-level C implementation of a wavetable synthesizer.
 * Generates audio tones (sine, saw, square) by linearly interpolating
 * over a pre-computed lookup table to save CPU cycles. Zero mock.
 */

#include <stdint.h>
#include <stdlib.h>
#include <math.h>

#define OMNI_WAVETABLE_SIZE 2048
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    WAVE_SINE,
    WAVE_SAW,
    WAVE_SQUARE
} OmniWaveShape;

typedef struct {
    float table[OMNI_WAVETABLE_SIZE];
    float phase;       // Current index in the table
    float phase_inc;   // Step size per sample
    float sample_rate;
} OmniWavetableOsc;

// Initialize a wavetable with a specific shape
void omni_wavetable_init(OmniWavetableOsc* osc, float sample_rate, OmniWaveShape shape) {
    osc->phase = 0.0f;
    osc->phase_inc = 0.0f;
    osc->sample_rate = sample_rate;

    for (int i = 0; i < OMNI_WAVETABLE_SIZE; i++) {
        float normalized_phase = (float)i / OMNI_WAVETABLE_SIZE;
        
        switch (shape) {
            case WAVE_SINE:
                osc->table[i] = sinf(2.0f * M_PI * normalized_phase);
                break;
            case WAVE_SAW:
                // Sawtooth from -1.0 to 1.0
                osc->table[i] = 2.0f * normalized_phase - 1.0f;
                break;
            case WAVE_SQUARE:
                // Square wave
                osc->table[i] = (normalized_phase < 0.5f) ? 1.0f : -1.0f;
                break;
        }
    }
}

// Set target frequency
void omni_wavetable_set_freq(OmniWavetableOsc* osc, float freq_hz) {
    // phase_inc = (TableSize * Freq) / SampleRate
    osc->phase_inc = (OMNI_WAVETABLE_SIZE * freq_hz) / osc->sample_rate;
}

// Generate the next audio sample
float omni_wavetable_process(OmniWavetableOsc* osc) {
    // Linear interpolation
    int index0 = (int)osc->phase;
    int index1 = (index0 + 1) % OMNI_WAVETABLE_SIZE;
    float frac = osc->phase - (float)index0;

    float val0 = osc->table[index0];
    float val1 = osc->table[index1];
    
    float out = val0 + frac * (val1 - val0);

    // Advance phase
    osc->phase += osc->phase_inc;
    if (osc->phase >= (float)OMNI_WAVETABLE_SIZE) {
        osc->phase -= (float)OMNI_WAVETABLE_SIZE;
    }

    return out;
}

// Generate a block of samples (vectorizable)
void omni_wavetable_process_block(OmniWavetableOsc* osc, float* output_buffer, int num_samples) {
    for (int i = 0; i < num_samples; i++) {
        output_buffer[i] = omni_wavetable_process(osc);
    }
}
