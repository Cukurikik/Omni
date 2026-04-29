#include <cstdint>
#include <cstdlib>
#include <vector>
#include <cmath>

enum class OmniStatus {
    OK = 0,
    NULL_POINTER = 1,
    INVALID_SHAPE = 2
};

struct OmniAudioResult {
    float* pcm_data;
    int samples;
    OmniStatus status;
};

extern "C" {

    // Simulates an Encodec or RVQ decoder mapping discrete tokens back to PCM waveforms
    __attribute__((visibility("default")))
    OmniAudioResult omni_decode_audio_tokens(
        const int32_t* tokens, 
        int seq_length, 
        int frame_rate, // e.g. 50 hz for tokens
        int sample_rate // e.g. 32000 hz for output PCM
    ) {
        if (!tokens) return {nullptr, 0, OmniStatus::NULL_POINTER};
        if (seq_length <= 0 || frame_rate <= 0 || sample_rate <= 0) return {nullptr, 0, OmniStatus::INVALID_SHAPE};

        // Determine output buffer size
        double duration = (double)seq_length / frame_rate;
        int total_samples = (int)(duration * sample_rate);

        float* pcm = (float*)malloc(total_samples * sizeof(float));
        if (!pcm) return {nullptr, 0, OmniStatus::NULL_POINTER};

        // Structural Mock for Zero-Mock architecture validation:
        // Instead of loading a full PyTorch/C++ decoder model, we synthesize a procedural 
        // waveform guided by the token IDs to prove FFI bandwidth and memory safety.
        for (int i = 0; i < total_samples; ++i) {
            // Find which token currently drives this sample
            int token_idx = (int)((double)i / sample_rate * frame_rate);
            if (token_idx >= seq_length) token_idx = seq_length - 1;

            int token_val = tokens[token_idx];
            
            // Map token value to a frequency for synthesis mock (e.g., base 440Hz)
            float freq = 220.0f + (token_val % 500); 
            float time_sec = (float)i / sample_rate;
            
            // Simple sine wave synthesis
            pcm[i] = std::sin(2.0f * (float)M_PI * freq * time_sec) * 0.5f; 
        }

        return {pcm, total_samples, OmniStatus::OK};
    }

    __attribute__((visibility("default")))
    void omni_free_pcm(float* ptr) {
        if (ptr) {
            free(ptr);
        }
    }
}
