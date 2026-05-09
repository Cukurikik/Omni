/*
 * omni_dynamic_compressor.c — Dynamic Range Compressor
 * Layer: Compute / Audio
 *
 * Implements a feed-forward audio Dynamic Range Compressor.
 * Attenuates signal peaks that exceed a set threshold, preventing clipping
 * while raising the overall perceived loudness of the audio stream. Zero mock.
 */

#include <math.h>

typedef struct {
    float threshold_db;
    float ratio;
    float attack_time;  // ms
    float release_time; // ms
    float makeup_gain_db;
    
    // Internal state
    float sample_rate;
    float attack_coeff;
    float release_coeff;
    float envelope;
} OmniCompressor;

// Converts Decibels to linear gain multiplier
static inline float db_to_linear(float db) {
    return powf(10.0f, db / 20.0f);
}

// Converts linear amplitude to Decibels
static inline float linear_to_db(float lin) {
    if (lin < 1e-5f) return -100.0f; // Floor
    return 20.0f * log10f(lin);
}

void omni_compressor_init(OmniCompressor* comp, float sample_rate) {
    comp->threshold_db = -20.0f;
    comp->ratio = 4.0f;          // 4:1 compression
    comp->attack_time = 10.0f;   // 10ms
    comp->release_time = 100.0f; // 100ms
    comp->makeup_gain_db = 0.0f;
    
    comp->sample_rate = sample_rate;
    comp->envelope = 0.0f;
    
    // Calculate filter coefficients for envelope tracker
    comp->attack_coeff = expf(-1.0f / (comp->attack_time * 0.001f * sample_rate));
    comp->release_coeff = expf(-1.0f / (comp->release_time * 0.001f * sample_rate));
}

// Process a single audio sample
float omni_compressor_process(OmniCompressor* comp, float input_sample) {
    // 1. Convert input to dB (absolute value)
    float input_db = linear_to_db(fabsf(input_sample));
    
    // 2. Calculate gain reduction needed
    float target_gain_db = 0.0f;
    if (input_db > comp->threshold_db) {
        // Exceeds threshold. We need to compress the overshoot.
        float overshoot = input_db - comp->threshold_db;
        // Gain reduction = Overshoot - (Overshoot / Ratio)
        // Since we want the target gain as a negative dB value:
        target_gain_db = -(overshoot * (1.0f - 1.0f / comp->ratio));
    }
    
    // 3. Smooth the gain reduction using attack/release envelope
    if (target_gain_db < comp->envelope) {
        // Attack phase (gain reduction is increasing, value is going more negative)
        comp->envelope = comp->attack_coeff * comp->envelope + (1.0f - comp->attack_coeff) * target_gain_db;
    } else {
        // Release phase (gain reduction is decreasing)
        comp->envelope = comp->release_coeff * comp->envelope + (1.0f - comp->release_coeff) * target_gain_db;
    }
    
    // 4. Apply total gain (Envelope + Makeup)
    float total_gain_db = comp->envelope + comp->makeup_gain_db;
    float linear_gain = db_to_linear(total_gain_db);
    
    return input_sample * linear_gain;
}

// Process a block of audio (in-place)
void omni_compressor_process_block(OmniCompressor* comp, float* buffer, int num_samples) {
    for (int i = 0; i < num_samples; i++) {
        buffer[i] = omni_compressor_process(comp, buffer[i]);
    }
}
