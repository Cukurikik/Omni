/*
 * omni_biquad_filter.c — Digital Biquad IIR Filter
 * Layer: Compute / Audio
 *
 * Implements a standard biquadratic filter (Infinite Impulse Response)
 * used for digital EQ, Low-Pass, High-Pass, and Band-Pass audio processing.
 * Direct Form 1 implementation for floating-point stability. Zero mock.
 */

#include <math.h>
#include <stdint.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    // Coefficients
    float a0, a1, a2;
    float b0, b1, b2;
    
    // State memory (z^-1, z^-2)
    float x1, x2;
    float y1, y2;
} OmniBiquadFilter;

// Core Direct Form 1 processing function
float omni_biquad_process(OmniBiquadFilter* f, float x) {
    // y[n] = (b0/a0)*x[n] + (b1/a0)*x[n-1] + (b2/a0)*x[n-2] 
    //        - (a1/a0)*y[n-1] - (a2/a0)*y[n-2]
    
    float y = (f->b0 / f->a0) * x 
            + (f->b1 / f->a0) * f->x1 
            + (f->b2 / f->a0) * f->x2 
            - (f->a1 / f->a0) * f->y1 
            - (f->a2 / f->a0) * f->y2;

    // Shift state history
    f->x2 = f->x1;
    f->x1 = x;
    
    f->y2 = f->y1;
    f->y1 = y;

    return y;
}

// Resets internal state to prevent clicking
void omni_biquad_reset(OmniBiquadFilter* f) {
    f->x1 = 0.0f; f->x2 = 0.0f;
    f->y1 = 0.0f; f->y2 = 0.0f;
}

// Calculate coefficients for a Low-Pass Filter (Audio EQ standard formula)
void omni_biquad_set_lpf(OmniBiquadFilter* f, float sample_rate, float cutoff_freq, float q_factor) {
    float w0 = 2.0f * M_PI * cutoff_freq / sample_rate;
    float alpha = sinf(w0) / (2.0f * q_factor);
    float cos_w0 = cosf(w0);

    f->b0 = (1.0f - cos_w0) / 2.0f;
    f->b1 = 1.0f - cos_w0;
    f->b2 = (1.0f - cos_w0) / 2.0f;
    
    f->a0 = 1.0f + alpha;
    f->a1 = -2.0f * cos_w0;
    f->a2 = 1.0f - alpha;
}

// Calculate coefficients for a High-Pass Filter
void omni_biquad_set_hpf(OmniBiquadFilter* f, float sample_rate, float cutoff_freq, float q_factor) {
    float w0 = 2.0f * M_PI * cutoff_freq / sample_rate;
    float alpha = sinf(w0) / (2.0f * q_factor);
    float cos_w0 = cosf(w0);

    f->b0 = (1.0f + cos_w0) / 2.0f;
    f->b1 = -(1.0f + cos_w0);
    f->b2 = (1.0f + cos_w0) / 2.0f;
    
    f->a0 = 1.0f + alpha;
    f->a1 = -2.0f * cos_w0;
    f->a2 = 1.0f - alpha;
}
