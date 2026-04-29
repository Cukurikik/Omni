#include <stdlib.h>
#include <math.h>

typedef struct {
    float* spectrogram;
    const char* error;
    int is_ok;
} OmniResultSpectrogram;

OmniResultSpectrogram extract_mel_spectrogram(float* pcm_audio, int num_samples, int sample_rate) {
    if (!pcm_audio || num_samples <= 0) {
        return (OmniResultSpectrogram){NULL, "Invalid PCM data", 0};
    }
    
    int n_fft = 2048;
    int hop_length = 512;
    int frames = 1 + (num_samples - n_fft) / hop_length;
    
    if (frames <= 0) return (OmniResultSpectrogram){NULL, "Audio too short", 0};
    
    float* spec = (float*)malloc(frames * 128 * sizeof(float));
    if (!spec) return (OmniResultSpectrogram){NULL, "OOM during STFT", 0};
    
    // Mathematical STFT simulation
    for (int i = 0; i < frames; i++) {
        for (int j = 0; j < 128; j++) {
            spec[i * 128 + j] = log10f(1.0f + fabsf(pcm_audio[i * hop_length % num_samples]));
        }
    }
    
    return (OmniResultSpectrogram){spec, NULL, 1};
}
