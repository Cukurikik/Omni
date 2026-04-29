#include <cmath>

extern "C" {
    void omni_sys_mossspeech_resample(const float* in_audio, int in_len, float* out_audio, int out_len) {
        if (!in_audio || !out_audio || in_len <= 0 || out_len <= 0) return;
        
        // Linear interpolation resampling
        float ratio = (float)(in_len - 1) / (out_len - 1);
        
        for (int i = 0; i < out_len; ++i) {
            float src_idx = i * ratio;
            int idx1 = (int)src_idx;
            int idx2 = std::min(idx1 + 1, in_len - 1);
            float frac = src_idx - idx1;
            
            out_audio[i] = in_audio[idx1] * (1.0f - frac) + in_audio[idx2] * frac;
        }
    }
}
